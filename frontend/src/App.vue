<template>
  <div id="app">
    <el-container>
      <el-header>
        <el-menu
            :default-active="activeIndex"
            class="el-menu-demo"
            mode="horizontal"
        >
          <li tabindex="0" class="el-menu-item" style="cursor: auto">
            <img height="60px" src="./assets/logo-dark.png"/>
          </li>
          <el-menu-item index="1">
            <router-link to="/">主页</router-link>
          </el-menu-item>

          <el-submenu v-if="user_info['code'] === 0" index="2">
            <template slot="title">{{ user_info["data"]["username"] }}</template>
            <router-link to="/profile">
              <el-menu-item index="2-1">个人空间</el-menu-item>
            </router-link>
            <router-link to="/profile/edit">
              <el-menu-item index="2-2">修改个人资料</el-menu-item>
            </router-link>
            <el-menu-item @click="event_logout()">登出</el-menu-item>
          </el-submenu>

          <el-menu-item v-else index="2">
            <router-link to="/login">登录</router-link>
          </el-menu-item>
        </el-menu>
      </el-header>
      <el-main style="margin: 0 auto">
        <router-view></router-view>
      </el-main>
      <el-footer class="oj-footer">
        <h6>{{ app_name }} · Powered by <a href="//github.com/XtherDevTeam/zqhf-oj-v2">zqhf-oj-v2</a></h6>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import axios from "axios";

export default {
  methods: {
    event_logout() {
      axios.get("/api/v1/user/logout").then((response) => {
        console.log(response)
        window.location.reload();
      });
    },
    init() {
      console.log(this.user_info);
      axios
          .get("/api/v1/user/details", {
            params: {},
          })
          .then((response) => {
            this.user_info = response.data;
            this.logged_in = response.data['code'] === 0;
          })
          .catch(function (error) {
            console.log(error);
          });
    },
  },
  data() {
    return {
      activeIndex: "1",
      activeIndex2: "1",
      logged_in: false,
      user_info: {},
      app_name: "肇庆华附在线评测系统",
    };
  },
  created: function () {
    this.init();
  },
};
</script>

<style>
#app {
  font-family: Helvetica, sans-serif;
}

a {
  text-decoration: none;
}

.oj-footer {
  height: 30px;
  text-align: center;
}
</style>
