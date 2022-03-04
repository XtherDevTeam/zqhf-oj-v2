<template>
  <div style="width: 500px; margin: 0 auto;text-align: center;">
    <div id="EventShowArea"></div>
    <el-card shadow="hover" class="login-box">
      <div slot="header" class="clearfix">
        <span class="align-text">注册</span>
      </div>
      <el-input v-model="usernameInput" placeholder="请输入用户名"></el-input>
      <div style="margin: 20px 0"></div>
      <el-input
          placeholder="请输入密码"
          v-model="passwordInput"
          show-password
      ></el-input>
      <div style="margin: 20px 0"></div>
      <el-button type="primary" @click="handleRegisterEvent()">注册</el-button>
      <div style="margin: 20px 0"></div>
      <span>或者...<el-link href="/#/login">去登陆</el-link>?</span>
    </el-card>
  </div>
</template>

<script>
import axios from "axios";
import App from "../App.vue";
import Vue from "vue";

export default {
  components: {App},
  methods: {
    handleRegisterEvent() {
      axios.post(
          "/api/v1/user/register/" + this.usernameInput + "/" + this.passwordInput
      ).then((response) => {
        if (response.data["code"] !== 0) {
          let Message = Vue.extend({
            template:
                '<el-alert id="EventShowArea" style="text-align: left;width: 100%;" title="注册失败!" type="error" description="代码' +
                response.data["code"] +
                ":" +
                response.data["text"] +
                '" show-icon ></el-alert> ',
          });
          new Message().$mount('#EventShowArea');
        } else {
          let Message = Vue.extend({
            template:
                '<el-alert id="EventShowArea" title="注册成功!" type="success" description="正在重定向到登录页 ..." show-icon ></el-alert> ',
          });
          new Message().$mount('#EventShowArea');
          setTimeout(() => {
            window.location = '/#/login';
          }, 1000);
        }
      });
    },
  },
  data() {
    return {
      usernameInput: "",
      passwordInput: "",
      input: "",
    };
  },
};
</script>

<style>
a {
  text-decoration: none;
}

.text {
  font-size: 14px;
}

.item {
  margin-bottom: 18px;
}

.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}

.clearfix:after {
  clear: both;
}
</style>
