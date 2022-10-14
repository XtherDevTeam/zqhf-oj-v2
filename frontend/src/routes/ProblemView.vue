<template>
  <div>
    <el-card shadow="hover" class="box-card">
      <div slot="header" class="clearfix">
        <span>{{ problem_content['name'] }}</span>
      </div>
      <el-tag><i class="el-icon-user-solid"></i> 作者: {{ problem_content['author'] }}</el-tag>
      <el-tag type="danger"><i class="el-icon-cpu"></i> 内存限制: {{ problem_content['memory'] }} kb</el-tag>
      <el-tag type="warning"><i class="el-icon-time"></i> 时间限制: {{ problem_content['timeout'] }} ms</el-tag>
      <el-tag type="success" v-if="problem_content['special_judge']">Special Judge: 是</el-tag>
      <el-tag type="info" v-else>Special Judge: 否</el-tag>
      <div style="margin: 10px auto;"></div>
      <span><i class="el-icon-s-platform"></i> 判题服务器: {{ judge_server_address }}</span>
      <div style="margin: 10px auto;"></div>
      <span><i class="el-icon-s-tools"></i> 支持语言: 
        <el-tag style="margin: 0 5px;" :key="i" v-for="i in support_judge_language">{{ i }}</el-tag>
      </span>
      <div style="margin: 10px auto;"></div>
      <span><strong>题目介绍: </strong></span><br>
      <div style="margin: 10px auto;"></div>
      <Markdown :code="problem_content['description']"></Markdown>

      <div style="margin: 10px auto;"></div>

      <span><strong>题目样例: </strong></span><br>
      <div style="margin: 10px auto;"></div>
      <div :key="index" v-for="example, index in problem_content['examples']">
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
      <el-select v-model="judge_lang" placeholder="选择提交语言" @change="switch_language">
        <el-option v-for="item in support_judge_language" :key="item" :label="item" :value="item"></el-option>
      </el-select>
      <el-button type="primary" @click="submit_judge">提交评测</el-button>

      <editor style="margin: 10px auto;" v-model="judge_answer" :language="editor_highlight_mode"
              width="100%" height="256px" @change="auto_save()"></editor>
    </el-card>
    <el-card shadow="hover" class="box-card" v-else>
      <span>登录后才能提交评测!</span><br>
    </el-card>
    <comment style="margin: 10px auto;" class="box-card" :area_id="'problem:'+this.problem_content['id']"></comment>
  </div>
</template>

<script>
import axios from "axios";
import MonacoEditor from "~/components/editor.vue";
import Comment from "~/components/comment.vue";
import Markdown from "~/components/markdown.vue";

export default {
  methods: {
    switch_language(item) {
      
      this.editor_highlight_mode = this.support_judge_language_highlight_mode[item];
      this.$message({
        type: "success",
        message: "this.editor_highlight_mode switch to " + this.editor_highlight_mode
      });
    },
    init() {
      axios.get("/api/v1/user/details", {
        params: {},
      }).then((response) => {
        this.user_info = response.data;
        this.logged_in = response.data['code'] === 0;
      }).catch(function (error) {
        
      });

      axios.get('/api/v1/problems/get/' + this.$route.query['id']).then((response) => {
        this.problem_content = response.data['data'];
        if (this.problem_content == null) {
          this.$message({
            type: "error",
            message: "题目内容拉取失败: " + response.data['text']
          });
        } else {
          this.problem_content['tags'] = JSON.parse(this.problem_content['tags']);
          this.problem_content['examples'] = JSON.parse(this.problem_content['examples']);
        }
      });
      axios.get('/api/v1/judge/info').then((response) => {
        this.support_judge_language = response.data['data']['judge-sever-support-language'];
        this.support_judge_language_highlight_mode = response.data['data']['judge-server-language-highlight-mode'];
        this.support_judge_language_exts = response.data['data']['judge-server-language-exts'];
        this.judge_server_address = response.data['data']['address']
      });

      if (window.localStorage.getItem("zqhf-oj-v2.code-auto-save.problem-" + this.$route.query['id']) !== null) {
        this.judge_answer = window.localStorage.getItem("zqhf-oj-v2.code-auto-save.problem-" + this.$route.query['id']);
      }
    },
    auto_save() {
      
      window.localStorage.setItem("zqhf-oj-v2.code-auto-save.problem-" + this.$route.query['id'], this.judge_answer);
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
    editor: MonacoEditor,
    comment: Comment,
    Markdown
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
      support_judge_language_highlight_mode: [],
      editor_highlight_mode: "cpp",
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