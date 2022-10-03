<template>
  <div style="margin: 0 auto;">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <el-col :span="20">
          <el-container >
            <el-aside width="40px"><el-avatar :size="40" :src="'/api/v1/user/image/get/' + show_user_info['data']['id']"></el-avatar></el-aside>
            <el-main style="padding: 10px;"><div style="font-size: 24px; display: inline-block;">{{ show_user_info['data']['username'] }}</div></el-main>
          </el-container>
        </el-col>
      </div>
      <div class="text item" v-if="show_user_info.data.other_message.permission_level !== -1">
          <el-tag type="warning"><i class="el-icon-s-flag"></i> Rating: {{ show_user_info['data']['ac_count'] }}</el-tag>
          <el-tag type="success"><i class="el-icon-s-data"></i> 全站排名: {{ show_user_info['data']['ranking'] }}</el-tag>

          <el-tag v-if="show_user_info.data.other_message.permission_level == 1" type="warning">Admin</el-tag>
          <el-tag v-else-if="show_user_info.data.other_message.permission_level == 2" type="danger">Super-admin</el-tag>
      </div>
      <div class="text item" v-else>
        <el-alert
            title="作弊者"
            description="该用户由于作弊、辱骂他人等不正当行为已被管理员封禁！"
            type="error"
            show-icon
            :closable="false"
          >
          </el-alert>
      </div>
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
    markdown_with_katex = require('@iktakahiro/markdown-it-katex');

markdown.use(markdownItHighlight);
markdown.use(markdown_with_katex);

export default {
  methods: {
    init() {
      
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
