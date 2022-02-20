<template>
  <div>
    <div id="EventShowArea"></div>
    <el-card class="login-box">
      <div slot="header" class="clearfix">
        <span class="align-text">登陆</span>
      </div>
      <el-input v-model="usernameInput" placeholder="请输入用户名"></el-input>
      <div style="margin: 20px 0"></div>
      <el-input
        placeholder="请输入密码"
        v-model="passwordInput"
        show-password
      ></el-input>
      <div style="margin: 20px 0"></div>
      <el-button type="primary" @click="handleLoginEvent()">登录</el-button
      ><br />
    </el-card>
  </div>
</template>

<script>
import axios from "axios";
import App from "../App.vue";
import Vue from "vue";

export default {
  components: { App },
  methods: {
    handleLoginEvent() {
      console.log("username: ", this.usernameInput);
      console.log("password: ", this.passwordInput);
      console.log(
        "bulit url is: ",
        "/api/v1/user/login/" + this.usernameInput + "/" + this.passwordInput
      );
      axios
        .post(
          "/api/v1/user/login/" + this.usernameInput + "/" + this.passwordInput
        )
        .then((response) => {
          if (response.data["code"] != 0) {
            var Message = Vue.extend({
              template:
                '<el-alert id="EventShowArea" title="登陆失败!" type="error" description="代码' +
                response.data["code"] +
                ":" +
                response.data["text"] +
                '" show-icon ></el-alert> ',
            });
            new Message().$mount('#EventShowArea');
          } else {
            var Message = Vue.extend({
              template:
                '<el-alert id="EventShowArea" title="登陆成功!" type="success" description="正在重定向到主页..." show-icon ></el-alert> ',
            });
            new Message().$mount('#EventShowArea');
            setTimeout( () => {
              window.location = '/';
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

.login-box {
  width: 480px;
}
</style>
