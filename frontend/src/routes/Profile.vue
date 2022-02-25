<template>
  <div style="margin: 0 auto;">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>{{ user_info['data']['username'] }}</span>
      </div>
      <div class="text item"><span>通过题目数: {{ user_info['data']['ac_count'] }}</span></div>
      <div class="text item"><span>介绍: {{ user_info['data']['introduction'] }}</span></div>
      <div v-html="full_introduction_rendered"></div>
    </el-card>
  </div>
</template>

<script>
import axios from "axios";
import Vue from "vue";


const markdown = require('markdown-it')(),
    markdown_with_katex = require('markdown-it-katex');

markdown.use(markdown_with_katex)

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
            this.logged_in = response.data['code'] === 0;
            if (this.logged_in) {
              console.log('logged in: ', this.user_info['data']['username'], this.user_info['data']['full_introduction']);
              this.full_introduction_rendered = markdown.render(this.user_info['data']['full_introduction']);
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
    };
  },
  created: function () {
    this.init();
  }
};
</script>

<style scoped>

.box-card {
  margin: 0 auto;
  width: 500px;
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
