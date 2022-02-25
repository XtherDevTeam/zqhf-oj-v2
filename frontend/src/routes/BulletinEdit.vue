<template>
  <el-card class="box-card">
    <div slot="header" class="clearfix">
      <span>编辑个人信息</span>
    </div>
    <el-input placeholder="请输入内容" v-model="username">
      <template slot="prepend">用户名</template>
    </el-input>
    <el-input placeholder="简短的一句话~" v-model="introduction" style="margin: 10px auto;">
      <template slot="prepend">介绍</template>
    </el-input>
    <span style="margin: 10px auto;">长介绍(将显示在个人主页)</span>
    <editor style="margin: 10px auto;" v-model="full_introduction" @init="editorInit" lang="html" theme="chrome"
            width="100%" height="256px"></editor>
    <el-button type="primary" @click="submit_changes">提交</el-button>
  </el-card>
</template>

<script>
import axios from "axios";

export default {
  methods: {
    init() {
      console.log(this.user_info);
      axios.get("/api/v1/user/details", {
        params: {},
      }).then((response) => {
        this.user_info = response.data;
        this.logged_in = response.data['code'] === 0;
        this.username = response.data['data']['username'];
        this.introduction = response.data['data']['introduction'];
        this.full_introduction = response.data['data']['full_introduction'];
      }).catch(function (error) {
        console.log(error);
      });
    },
    editorInit() {
      require('brace/ext/language_tools') //language extension prerequisite...
      require('brace/mode/html')
      require('brace/mode/javascript')    //language
      require('brace/mode/less')
      require('brace/theme/chrome')
      require('brace/snippets/javascript') //snippet
    },
    submit_changes() {
      axios.post('/api/v1/user/change_info', {
        'username': this.username,
        'introduction': this.introduction,
        'full_introduction': this.full_introduction
      }).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: "error",
            message: "[" + response['code'] + "] " + response.data['text'] + " 上传用户信息失败"
          });
        } else {
          window.location = '/#/';
        }
      })
    }
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      edit_content: "",
      username: "",
      introduction: "",
      full_introduction: "",
    }
  },
  components: {
    editor: require('vue2-ace-editor'),
  },
  mounted() {
    this.init();
  }
};
</script>

<style scoped>

</style>