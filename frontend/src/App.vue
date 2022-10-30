<template>
  <div id="app" style="width: 100%;">
    <el-container>
      <el-header id="app-header" class="header-custom is-fixed" style="overflow: hidden;">
        <el-menu
            :default-active="activeIndex"
            class="el-menu-demo"
            id="app-menu"
            mode="horizontal"
        >
          <li style="float: left;" height="56px" role="menuitem"><img height="56px" src="./assets/logo-new.png"/></li>
          <el-menu-item index="1">
            <el-link href="/#/">主页</el-link>
          </el-menu-item>

          <el-menu-item index="2">
            <el-link href="/#/problems">题库</el-link>
          </el-menu-item>

          <el-menu-item index="3">
            <el-link href="/#/lists">题单列表</el-link>
          </el-menu-item>

          <el-menu-item index="4">
            <el-link href="/#/contests">比赛列表</el-link>
          </el-menu-item>

          <el-menu-item index="5">
            <el-link href="/#/records">评测记录</el-link>
          </el-menu-item>

          <el-menu-item index="6">
            <el-link href="/#/articles">文章列表</el-link>
          </el-menu-item>

          <el-menu-item index="7">
            <el-link href="/#/ide">在线IDE</el-link>
          </el-menu-item>

          <el-menu-item index="8">
            <el-link href="/#/machines">评测机列表</el-link>
          </el-menu-item>

          <el-submenu v-if="user_info['code'] === 0" index="9">
            <template slot="title">{{ user_info["data"]["username"] }}</template>
            <el-menu-item index="2-1">
              <el-link href="/#/profile">个人空间</el-link>
            </el-menu-item>
            <el-menu-item index="2-2">
              <el-link href="/#/profile/edit">修改个人资料</el-link>
            </el-menu-item>
            <el-menu-item index="2-3" @click="change_password_dialog_visible = true;">修改密码</el-menu-item>
            <el-menu-item @click="event_logout()">登出</el-menu-item>
          </el-submenu>

          <el-menu-item v-else index="9">
            <el-link href="/#/login">登录</el-link>
          </el-menu-item>
        </el-menu>
      </el-header>
      <el-main style="margin: 0 auto;" id="app-container">
        <div class="ui main-container" style="height: 100%; ">
          <el-dialog v-if="logged_in" title="修改密码" :visible.sync="change_password_dialog_visible" width="50%">
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
        <h6>{{ app_name }} · Powered by
          <el-link href="//github.com/XtherDevTeam/zqhf-oj-v2">zqhf-oj-v2</el-link>
        </h6>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import axios from "axios";
import utils from "~/utils.js"

export default {
  methods: {
    event_logout() {
      axios.get("/api/v1/user/logout").then((response) => {
        
        window.location.reload();
      });
    },
    init() {
      this.init_copy_btn();
      axios
          .get("/api/v1/user/details", {
            params: {},
          })
          .then((response) => {
            this.user_info = response.data;
            this.logged_in = response.data['code'] === 0;
          })
          .catch(function (error) {
            
          });
          document.getElementById('app-header').classList.add('is-visible');
      var agent = navigator.userAgent;
      if (/.*Firefox.*/.test(agent)) {
          document.addEventListener("DOMMouseScroll", function(e) {
              e = e || window.event;
              var detail = e.detail;
              if (detail > 0) {
                document.getElementById('app-header').classList.remove('is-visible');
              } else {
                document.getElementById('app-header').classList.add('is-visible');
              }
          });
      } else {
          document.onmousewheel = function(e) {
              e = e || window.event;
              var wheelDelta = e.wheelDelta;
              if (wheelDelta > 0) {
                document.getElementById('app-header').classList.add('is-visible');
              } else {
                document.getElementById('app-header').classList.remove('is-visible');
              }
          }
      }
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
            
          });
    },
    init_copy_btn() {
      let _this = this;
      let clipboard = new this.clipboard(".copy-btn");
      clipboard.on('success', function () {
        _this.$message({type: "success", message: "复制成功!"});
      });
      clipboard.on('error', function () {
        _this.$message({type: "error", message: "复制失败!"});
      });
    },
  },
  data() {
    return {
      activeIndex: "1",
      activeIndex2: "1",
      logged_in: false,
      user_info: {},
      app_name: utils.getAppName(),
      change_password_dialog_visible: false,
      change_password_new_password: "",
      change_password_origin_password: ""
    };
  },
  mounted: function () {
    this.init();
  }
};
</script>

<style>
</style>
