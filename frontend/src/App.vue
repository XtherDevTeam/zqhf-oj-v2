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
            <a href="/#/">主页</a>
          </el-menu-item>

          <el-submenu v-if="user_info['code'] === 0" index="2">
            <template slot="title">{{ user_info["data"]["username"] }}</template>
            <el-menu-item index="2-1"><a href="/#/profile">个人空间</a></el-menu-item>
            <el-menu-item index="2-2"><a href="/#/profile/edit">修改个人资料</a></el-menu-item>
            <el-menu-item index="2-3" @click="change_password_dialog_visible = true;">修改密码</el-menu-item>
            <el-menu-item @click="event_logout()">登出</el-menu-item>
          </el-submenu>

          <el-menu-item v-else index="2">
            <a href="/#/login">登录</a>
          </el-menu-item>
        </el-menu>
      </el-header>
      <el-main style="margin: 0 auto;">
        <div class="ui main-container" style="height: 100%; ">
          <el-dialog v-if="logged_in" title="修改密码" :visible.sync="change_password_dialog_visible" width="30%">
            <span>正在修改 {{ user_info['data']['username'] }} 的密码</span>
            <div style="margin: 10px;"></div>
            <el-input placeholder="请输入原密码" v-model="change_password_origin_password" show-password></el-input>
            <div style="margin: 10px;"></div>
            <el-input placeholder="新密码" v-model="change_password_new_password" show-password></el-input>
            <span slot="footer" class="dialog-footer">
              <el-button @click="change_password_dialog_visible = false">取 消</el-button>
              <el-button type="primary" @click="event_change_password">确 定</el-button>
            </span>
          </el-dialog>
          <router-view></router-view>
        </div>
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
    event_change_password() {
      axios
          .post("/api/v1/user/change_password", {
            old_password: this.change_password_origin_password,
            new_password: this.change_password_new_password
          })
          .then((response) => {
            if (response.data['code'] === 0) {
              this.$message({type: "success", message: "修改成功!"});
              this.change_password_dialog_visible = false;
            } else {
              this.$message({
                type: "error",
                message: '[' + response.data['code'] + '] ' + response.data['text'] + ' 修改失败'
              });
            }
          })
          .catch(function (error) {
            console.log(error);
          });
    }
  },
  data() {
    return {
      activeIndex: "1",
      activeIndex2: "1",
      logged_in: false,
      user_info: {},
      app_name: "肇庆华附在线评测系统",
      change_password_dialog_visible: false,
      change_password_new_password: "",
      change_password_origin_password: "",
    };
  },
  mounted: function () {
    this.init();
  },
};
</script>

<style>
#app {
  font-family: Helvetica, sans-serif;
}

.katex .vlist {
  display: table-cell;
  position: relative;
  vertical-align: unset;
}

.ui.main-container {
  width: 933px;
  margin: 0 auto;
}

@media only screen and (min-width: 1200px) {
  .ui.main-container {
    width: 1127px;
    margin-left: auto !important;
    margin-right: auto !important;
  }
}

@media only screen and (min-width: 1500px) {
  .ui.main-container {
    width: 1512px;
    margin-left: auto !important;
    margin-right: auto !important;
  }
}

@media only screen and (max-width: 767px) {
  .ui.main-container {
    width: auto !important;
    margin-left: 1em !important;
    margin-right: 1em !important
  }
}

@media only screen and (min-width: 768px) and (max-width: 991px) {
  .ui.main-container {
    width: 723px;
    margin-left: auto !important;
    margin-right: auto !important
  }
}


a {
  text-decoration: none;
}

.oj-footer {
  height: 30px;
  text-align: center;
}
</style>
