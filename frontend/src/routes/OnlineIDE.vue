<template>
  <div>
    <el-dialog width="90%" style="margin: 0 auto;" title="运行程序" :visible.sync="run_dialog_visible">
      <el-container style="width: 100%;">
        <el-aside width="50%">
          <span>输入</span>
          <editor style="margin: 10px auto;" v-model="stdin" :language="editor_highlight_mode"
              width="100%" height="400px"></editor>
        </el-aside>
        <el-main style="padding: unset;">
          <span>输出</span>
          <editor style="margin: 10px auto;" v-model="stdout" :language="editor_highlight_mode"
              :readonly="true" width="100%" height="400px"></editor>
        </el-main>
      </el-container>
      
      <span slot="footer" class="dialog-footer">
        <el-button @click="run_dialog_visible = false">取 消</el-button>
        <el-button type="primary" @click="submit" v-bind:disabled="judging">运行</el-button>
      </span>
    </el-dialog>
    <el-card shadow="hover" class="box-card" style="width: 100%; height: fit-content(100%);" v-if="logged_in">
      <div slot="header" class="clearfix">
        <span>在线IDE</span>
      </div>
      <div style="margin: 10px auto;"></div>
      <span>代码</span>
      <editor style="margin: 10px auto;" v-model="judge_answer" :language="editor_highlight_mode"
          width="100%" height="512px" @change="auto_save()"></editor>
      <div style="margin: 10px auto;"></div>
      <el-select v-model="judge_lang" placeholder="选择语言" @change="switch_language">
        <el-option v-for="item in support_judge_language" :key="item" :label="item" :value="item"></el-option>
      </el-select>
      <el-button type="primary" @click="run_dialog_visible = true;">运行</el-button>
    </el-card>
    <el-card shadow="hover" class="box-card" style="width=100%;" v-else>
      <div slot="header" class="clearfix">
        <span>在线IDE</span>
      </div>
      <span>请先登录</span>
    </el-card>
  </div>
</template>

<script>
import axios from "axios";
import MonacoEditor from "../components/editor.vue";

import markdownItHighlight from 'markdown-it-highlight';

const markdown = require('markdown-it')(),
    markdown_with_katex = require('@iktakahiro/markdown-it-katex');

markdown.use(markdownItHighlight);
markdown.use(markdown_with_katex);

export default {
  methods: {
    switch_language(item) {
      
      this.editor_highlight_mode = this.support_judge_language_highlight_mode[item];
      this.$message({
        type: "success",
        message: "this.editor_highlight_mode switch to " + this.editor_highlight_mode
      });
    },
    auto_save() {
      window.localStorage.setItem("zqhf-oj-v2.code-auto-save.online-ide", this.judge_answer);
    },
    init() {
      axios.get("/api/v1/user/details", {
        params: {},
      }).then((response) => {
        this.user_info = response.data;
        this.logged_in = response.data['code'] === 0;
      }).catch(function (error) {
        
      });
      axios.get('/api/v1/judge/info').then((response) => {
        this.support_judge_language = response.data['data']['judge-sever-support-language'];
        this.support_judge_language_highlight_mode = response.data['data']['judge-server-language-highlight-mode'];
        this.support_judge_language_exts = response.data['data']['judge-server-language-exts'];
        this.judge_server_address = response.data['data']['address'];
        
      });
      if (window.localStorage.getItem("zqhf-oj-v2.code-auto-save.online-ide") !== null) {
        this.judge_answer = window.localStorage.getItem("zqhf-oj-v2.code-auto-save.online-ide");
      }
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
      axios.post('/api/v1/judge/submit', param).then((response) => {
        this.judging = false;
        if (response.data.code !== 0) {
          this.$message({
            type: "error",
            message: "无法提交评测: " + response.data.text
          });
        } else {
          if(response.data['data']['status'].startsWith('Wrong Answer')) {
            this.stdout = `Status: OK\n\n`;
          } else {
            this.stdout = `Status: ${response.data['data']['status']}\n\n`;
          }
          this.stdout += 'Stderr>\n' + response.data['data']['stderr'] + '\n\nStdout>\n' + response.data['data']['stdout'] + '\n';
        }
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
      run_dialog_visible: false,
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