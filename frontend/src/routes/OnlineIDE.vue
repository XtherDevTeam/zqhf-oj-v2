<template>
  <el-card shadow="hover" class="box-card" style="width=100%;" v-if="logged_in">
    <div slot="header" class="clearfix">
      <span>在线IDE</span>
    </div>
    <div style="margin: 10px auto;"></div>
    <span>代码</span>
    <editor style="margin: 10px auto;" v-model="judge_answer" :language="editor_highlight_mode"
        width="100%" height="256px"></editor>
    <div style="margin: 10px auto;"></div>
    <span>输入</span>
    <editor style="margin: 10px auto;" v-model="stdin" :language="editor_highlight_mode"
        width="100%" height="128px"></editor>
    <div style="margin: 10px auto;"></div>
    <span>输出</span>
    <editor style="margin: 10px auto;" v-model="stdout" :language="editor_highlight_mode"
        width="100%" height="128px"></editor>
    <el-select v-model="judge_lang" placeholder="选择语言" @change="switch_language">
      <el-option v-for="item in support_judge_language" :key="item" :label="item" :value="item"></el-option>
    </el-select>
    <el-button type="primary" @click="submit" v-bind:disabled="judging">运行</el-button>
  </el-card>
  <el-card shadow="hover" class="box-card" style="width=100%;" v-else>
    <div slot="header" class="clearfix">
      <span>在线IDE</span>
    </div>
    <span>请先登录</span>
  </el-card>
</template>

<script>
import axios from "axios";
import MonacoEditor from "../components/editor.vue";
import Comment from "../components/comment.vue";

import markdownItHighlight from 'markdown-it-highlight';

const markdown = require('markdown-it')(),
    markdown_with_katex = require('@iktakahiro/markdown-it-katex');

markdown.use(markdownItHighlight);
markdown.use(markdown_with_katex);

export default {
  methods: {
    switch_language(item) {
      console.log(this.support_judge_language.indexOf(item));
      this.editor_highlight_mode = this.support_judge_language_highlight_mode[item];
      this.$message({
        type: "success",
        message: "this.editor_highlight_mode switch to " + this.editor_highlight_mode
      });
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
      axios.get('/api/v1/judge/info').then((response) => {
        this.support_judge_language = response.data['data']['support-languages'];
        this.support_judge_language_highlight_mode = response.data['data']['support-language-highlight-mode'];
        this.support_judge_language_exts = response.data['data']['support-language-exts'];
        this.judge_server_address = response.data['data']['address'];
        console.log(this.support_judge_language_exts);
      });
    },
    submit() {
      this.judging = true;
      let param = {
          'plugin': this.judge_lang,
          'source_file': this.judge_answer,
          'input': this.stdin,
          'output': '',
          'env_variables': {
            'source_file': 'temp.' + this.support_judge_language_exts[this.judge_lang],
            'binary_file': 'temp.bin'
          },
          'time_limit': 2000,
          'mem_limit': 1048576,
        };
      axios.post('/judge_api/ide_submit', param).then((response) => {
        this.judging = false;
        this.stdout = 'Stderr>\n' + response.data['stderr'] + '\n\nStdout>\n' + response.data['stdout'] + '\n';
      });
    }
  },
  components: {
    editor: MonacoEditor,
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
      support_judge_language_exts: [],
      editor_highlight_mode: "cpp",
      judge_server_address: "",
      judge_answer: "",
      judge_lang: "",
      stdin: "",
      stdout: "",
      judging: false,
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