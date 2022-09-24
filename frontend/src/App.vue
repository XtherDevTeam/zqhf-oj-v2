<template>
  <div id="app" style="width: 100%;">
    <el-container>
      <el-header id="app-header">
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
            <el-link href="/#/records">评测记录</el-link>
          </el-menu-item>

          <el-menu-item index="5">
            <el-link href="/#/articles">文章列表</el-link>
          </el-menu-item>

          <el-menu-item index="6">
            <el-link href="/#/ide">在线IDE</el-link>
          </el-menu-item>

          <el-menu-item index="7">
            <el-link href="/#/machines">评测机列表</el-link>
          </el-menu-item>

          <el-submenu v-if="user_info['code'] === 0" index="8">
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

          <el-menu-item v-else index="8">
            <el-link href="/#/login">登录</el-link>
          </el-menu-item>
        </el-menu>
      </el-header>
      <el-main style="margin: 0 auto;" id="app-container">
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
        <h6>{{ app_name }} · Powered by
          <el-link href="//github.com/XtherDevTeam/zqhf-oj-v2">zqhf-oj-v2</el-link>
        </h6>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import axios from "axios";
import MonacoEditor from "./components/editor.vue";
import 'markdown-it-highlight/dist/index.css';

export default {
  methods: {
    event_logout() {
      axios.get("/api/v1/user/logout").then((response) => {
        
        window.location.reload();
      });
    },
    init() {
      
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

      var agent = navigator.userAgent;
      if (/.*Firefox.*/.test(agent)) {
          document.addEventListener("DOMMouseScroll", function(e) {
              e = e || window.event;
              var detail = e.detail;
              if (detail > 0) {
                document.getElementById('app-header').style.visibility = 'hidden';
                document.getElementById('app-container').style.paddingTop = '0px';
              } else {
                document.getElementById('app-header').style.visibility = 'unset';
                document.getElementById('app-container').style.paddingTop = '82px';
              }
          });
      } else {
          document.onmousewheel = function(e) {
              e = e || window.event;
              var wheelDelta = e.wheelDelta;
              if (wheelDelta > 0) {
                  document.getElementById('app-header').style.visibility = 'unset';
                  document.getElementById('app-container').style.paddingTop = '82px';
              } else {
                document.getElementById('app-header').style.visibility = 'hidden';
                document.getElementById('app-container').style.paddingTop = '0px';
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
    }
  },
  data() {
    return {
      activeIndex: "1",
      activeIndex2: "1",
      logged_in: false,
      user_info: {},
      app_name: "肇庆华赋在线评测系统",
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
#app {
  font-family: Helvetica, sans-serif;
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


#app-header {
  border-bottom: 1px solid #E6E6E6;
  background: rgba(255, 255, 255, 0.24);
  -webkit-backdrop-filter: blur(300px);
  backdrop-filter: blur(300px);
  position: fixed;
  top: 0;
  width: 100%;
  z-index: 114514;
}

#app-container {
  padding-top: 82px;
}

#app-menu {
  background: rgba(0, 0, 0, 0);
  width: 100%;
  border-bottom: unset;
}
</style>
