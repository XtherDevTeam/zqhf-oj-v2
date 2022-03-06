<template>
  <div style="margin: 0 auto;">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>{{ show_user_info['data']['username'] }}</span>
      </div>
      <div class="text item"><span>通过题目数: {{ show_user_info['data']['ac_count'] }}</span></div>
      <div class="text item"><span>介绍: {{ show_user_info['data']['introduction'] }}</span></div>
      <div style="height: 10px;"></div>
      <div class="markdown-body" v-html="full_introduction_rendered"></div>
    </el-card>
  </div>
</template>

<script>
import axios from "axios";
import MonacoEditor from "../components/editor.vue";

import markdownItHighlight from 'markdown-it-highlight';

const markdown = require('markdown-it')(),
    markdown_with_katex = require('markdown-it-katex');

markdown.use(markdownItHighlight);
markdown.use(markdown_with_katex);

export default {
  methods: {
    init() {
      console.log(this.user_info);
      axios
          .get("/api/v1/user/details", {
            params: {},
          })
          .then((response) => {
            this.user_info = response.data;
            if (this.$route.query['id'] !== undefined) {
              axios.get("/api/v1/user/details?user_id=" + this.$route.query['id']).then((response) => {
                this.show_user_info = response.data;
                if (response.data['code'] !== 0) {
                  this.$message({
                    type: "error",
                    message: "[" + response.data['code'] + "] " + response.data['text'] + " 拉取用户信息失败!"
                  });
                } else {
                  this.full_introduction_rendered = markdown.render(this.show_user_info['data']['full_introduction']);
                }
              });
            } else {
              this.show_user_info = this.user_info;
              this.logged_in = response.data['code'] === 0;
              if (this.logged_in) {
                this.full_introduction_rendered = markdown.render(this.user_info['data']['full_introduction']);
              }
            }
          })
          .catch(function (error) {
            console.log(error);
          });
    }
  },
  data() {
    return {
      user_info: {},
      full_introduction_rendered: "",
      show_user_info: {},
    };
  },
  mounted: function () {
    this.init();
  }
};
</script>

<style scoped>

.box-card {
  margin: 0 auto;
  width: 1000px;
}

.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}

.clearfix:after {
  clear: both
}
</style>
