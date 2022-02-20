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
            <img height="60px" src="./assets/logo-dark.png" />
          </li>
          <el-menu-item index="1"><router-link to="/">主页</router-link></el-menu-item>

          <el-submenu v-if="user_info['code'] == 0" index="2">
            <template slot="title">{{
              user_info["data"]["username"]
            }}</template>
            <router-link to="/profile"><el-menu-item index="2-1">个人空间</el-menu-item></router-link>
            <router-link to="/profile/edit"><el-menu-item index="2-2">修改个人资料</el-menu-item></router-link>
            <el-menu-item @click="event_logout()">登出</el-menu-item>
          </el-submenu>

          <el-menu-item v-else index="2"><router-link to="/login">登录</router-link></el-menu-item>
        </el-menu>
      </el-header>
      <el-main style="margin: 0 auto">
        <router-view></router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import axios from "axios";

export default {
  methods: {
    event_logout() {
      axios.get("/api/v1/user/logout").then((response) => {
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
      logined: false,
      user_info: {},
    };
  },
  created: function () {
    console.log("草泥马傻逼玩意");
    this.init();
  },
};
</script>

<style>
#app {
  font-family: Helvetica, sans-serif;
}
#left-sidebar {
  width: 15%;
}
a {
  text-decoration: none;
}
</style>
