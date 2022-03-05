<template>
  <div>
    <el-card shadow="hover" class="box-card">
      <div slot="header" class="clearfix">
        <span>{{ problem_content['name'] }}</span><br>
        <span>作者: {{ problem_content['author'] }}</span>
        <span>内存限制: {{ problem_content['memory'] }} kb</span>
        <span>时间限制: {{ problem_content['timeout'] }} ms</span>
      </div>
      <span>使用判题服务器: {{ judge_server_address }}</span>
      <div style="margin: 10px auto;"></div>
      <span>支持语言: <el-tag style="margin: 0 5px;" :key="i" v-for="i in support_judge_language">{{ i }}</el-tag></span>
      <div style="margin: 10px auto;"></div>
      <span><strong>题目介绍: </strong></span><br>
      <div style="margin: 10px auto;"></div>
      <div class="markdown-body" id="markdownRenderedPlace" v-html="rendered_content"></div>

      <div style="margin: 10px auto;"></div>

      <span><strong>题目样例: </strong></span><br>
      <div style="margin: 10px auto;"></div>
      <div :key="example" v-for="example in problem_content['examples']">
        <el-container>
          <el-aside width="50%">
            输入:<br>
            <pre><code>{{ example['in'] }}</code>
          </pre>
          </el-aside>
          <el-main style="padding: unset;">
            输出:<br>
            <pre><code>{{ example['out'] }}</code>
          </pre>
          </el-main>
        </el-container>
      </div>
    </el-card>
    <div style="margin: 10px auto;"></div>
    <el-card v-if="logged_in" shadow="hover" class="box-card">
      <div slot="header" class="clearfix">
        <span>提交答案</span><br>
      </div>
      <el-select v-model="judge_lang" placeholder="选择提交语言">
        <el-option
            v-for="item in support_judge_language"
            :key="item"
            :label="item"
            :value="item">
        </el-option>
      </el-select>
      <el-button type="primary" @click="submit_judge">提交评测</el-button>

      <editor style="margin: 10px auto;" v-model="judge_answer" @init="editorInit" lang="c++" theme="chrome"
              width="100%" height="256px"></editor>
    </el-card>
    <el-card shadow="hover" class="box-card" v-else>
      <span>登录后才能提交评测!</span><br>
    </el-card>
  </div>
</template>

<script>
import axios from "axios";
import Vue from "_vue@2.6.14@vue";

import markdownItHighlight from 'markdown-it-highlight';

const markdown = require('markdown-it')(),
    markdown_with_katex = require('markdown-it-katex');

markdown.use(markdownItHighlight);
markdown.use(markdown_with_katex);

export default {
  methods: {
    editorInit() {
      require('brace/ext/language_tools') //language extension prerequisite...
      require('brace/mode/html')
      require('brace/mode/javascript')    //language
      require('brace/mode/less')
      require('brace/theme/chrome')
      require('brace/snippets/javascript') //snippet
    },
    init() {
      console.log(this.user_info);
      axios.get("/api/v1/user/details", {
        params: {},
      }).then((response) => {
        this.user_info = response.data;
        this.logged_in = response.data['code'] === 0;
      }).catch(function (error) {
        console.log(error);
      });

      axios.get('/api/v1/problems/get/' + this.$route.query['id']).then((response) => {
        this.problem_content = response.data['data'];
        if (this.problem_content == null) {
          this.$message({
            type: "error",
            message: "题目内容拉取失败!"
          });
        } else {
          this.problem_content['tags'] = JSON.parse(this.problem_content['tags']);
          this.problem_content['examples'] = JSON.parse(this.problem_content['examples']);
          this.rendered_content = markdown.render(this.problem_content['description']);
        }
      });

      axios.get('/api/v1/judge/info').then((response) => {
        this.support_judge_language = response.data['data']['support-languages'];
        this.judge_server_address = response.data['data']['address']
      });
    },
    submit_judge() {
      axios.post('/api/v1/problems/' + this.$route.query['id'] + '/judge/submit', {
        lang: this.judge_lang,
        code: this.judge_answer
      }).then((response) => {
        if (response.data["code"] !== 0) {
          this.$message({
            type: "error",
            message: '提交失败: 代码' + response.data["code"] + ":" +
                response.data["text"]
          });
        } else {
          window.location = '/#/records/view?id=' + response.data['data'];
        }
      })
    }
  },
  components: {
    editor: require('vue2-ace-editor'),
  },
  mounted() {
    this.init();
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      problem_content: "",
      rendered_content: "",
      support_judge_language: [],
      judge_server_address: "",
      judge_answer: "",
      judge_lang: "",
    }
  }
};
</script>

<style scoped>
.box-card {
  width: 70%;
  margin: 0 auto;
}
</style>