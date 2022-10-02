<template>
  <el-container>
    <el-dialog title="新建公告" :visible.sync="create_bulletin_dialog_visible" width="50%">
      <el-input placeholder="请输入内容" v-model="create_bulletin_dialog_name">
        <template slot="prepend">标题</template>
      </el-input>
      <div style="margin: 10px auto;"></div>
      <span style="margin: 10px auto;">公告内容</span>
      <editor style="margin: 10px auto;" v-model="create_bulletin_dialog_content" language="markdown"

              width="100%" height="256px"></editor>
      <span slot="footer" class="dialog-footer">
        <el-button @click="create_bulletin_dialog_visible = false">取 消</el-button>
        <el-button type="primary" @click="bulletins_create">确 定</el-button>
      </span>
    </el-dialog>
    <el-aside width="70%" style="padding: 20px;">
      <el-card shadow="hover" class="box-card">
        <div slot="header" class="clearfix">
          <span>欢迎来到{{ app_name }}！</span>
        </div>
        <img src="../assets/head-image.png" style="width: 100%;"/>
      </el-card>
      <el-card shadow="hover" style="margin: 10px auto;">
        <div slot="header" class="clearfix">
          <span>公告</span>
          <el-button v-if="logged_in && user_info['data']['other_message']['permission_level']"
                     style="float: right; padding: 3px 0" type="text"
                     @click="create_bulletin_dialog_visible = true">
            新建
          </el-button>
        </div>
        <el-table :data="bulletins" style="width: 100%" @row-click="bulletins_check">
          <el-table-column fixed prop="id" label="编号" width="64"></el-table-column>
          <el-table-column fixed prop="time" label="日期" width="200"></el-table-column>
          <el-table-column prop="name" label="名称"></el-table-column>
          <el-table-column fixed="right" label="操作" width="256">
            <template v-slot="scope">
              <el-button v-if="logged_in && user_info['data']['other_message']['permission_level']" type="text"
                         size="small" @click.native.stop="bulletins_edit(scope.row)">编辑
              </el-button>
              <el-button v-if="logged_in && user_info['data']['other_message']['permission_level']"
                         @click.native.stop="bulletins_delete(scope.row)" type="text" size="small">删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
      <el-card shadow="hover" style="margin: 10px auto;">
        <div slot="header" class="clearfix">
          <span>Rating · 前十</span>
          <el-button style="float: right; padding: 3px 0" type="text"
                     @click="goto_ratings()">
            查看全部
          </el-button>
        </div>
        <el-table :data="ranking_top10" style="width: 100%;" @row-click="profile_click">
          <el-table-column fixed prop="id" label="User ID" width="128"></el-table-column>
          <el-table-column fixed label="用户名">
            <template v-slot="scope">
              <el-avatar :size="25" :src="'/api/v1/user/image/get/' + scope.row.id"></el-avatar>
              <span style="margin: 2px 4px;position: absolute;">{{ scope.row.username }}</span>
            </template>
          </el-table-column>
          <el-table-column fixed prop="introduction" label="一句话介绍"></el-table-column>
          <el-table-column fixed prop="ac_count" label="Rating" width="64"></el-table-column>
          <el-table-column fixed prop="ranking" label="排名" width="64"></el-table-column>
        </el-table>
      </el-card>
    </el-aside>
    <el-main>
      <div v-if="logged_in === true">
        <el-card shadow="hover">
          <div slot="header" class="clearfix">
            <span>{{ user_info['data']['username'] }}</span>
          </div>
          <div class="text item">{{ user_info['data']['introduction'] }}</div>
          <div class="text item">
              <el-tag type="warning"><i class="el-icon-s-flag"></i> Rating: {{ user_info['data']['ac_count'] }}</el-tag>
              <el-tag type="success"><i class="el-icon-s-data"></i> 全站排名: {{ user_info['data']['ranking'] }}</el-tag>
          </div>
        </el-card>
        <el-card shadow="hover" style="margin: 10px auto;">
          <div slot="header" class="clearfix">
            <span>一言(ひとこと)</span>
          </div>
          <span>{{ hitokoto['hitokoto'] }}</span><br>
          <span>-- 《{{ hitokoto['from'] }}》 {{ hitokoto['from_who'] }}</span>
        </el-card>
        <el-card shadow="hover" style="margin: 10px auto;">
          <div slot="header" class="clearfix">
            <span>查找题目</span>
          </div>
          <el-input placeholder="请输入内容" v-model="search_input" class="input-with-select">
            <el-select v-model="search_select" slot="prepend" placeholder="请选择" style="width: 100px;">
              <el-option label="题号" value="by_id"></el-option>
              <el-option label="作者" value="by_author"></el-option>
              <el-option label="题面" value="by_description"></el-option>
              <el-option label="标签" value="by_tags"></el-option>
            </el-select>
            <el-button slot="append" icon="el-icon-search" @click="on_search_event"></el-button>
          </el-input>
          <el-table :data="search_result" style="width: 100%;height: auto;">
            <el-table-column prop="id" label="题号"></el-table-column>
            <el-table-column prop="name" label="名称"></el-table-column>
            <el-table-column fixed="right" label="操作">
              <template v-slot="scope">
                <el-button @click="problem_click(scope.row)" type="text" size="small">查看</el-button>
              </template>
            </el-table-column>

          </el-table>
        </el-card>
      </div>
      <div v-else>
        <el-card shadow="hover">
          <span>请先登录!</span>
        </el-card>
      </div>
    </el-main>
  </el-container>
</template>

<script>
import axios from "axios";
import MonacoEditor from "../components/editor.vue";

export default {
  methods: {
    init() {
      
      axios.get("/api/v1/user/details", {
        params: {},
      }).then((response) => {
        this.user_info = response.data;
        this.logged_in = response.data['code'] === 0;
      }).catch(function (error) {
        
      });
      axios.get("/api/v1/bulletins/get/0/10", {
        params: {},
      }).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: 'error',
            message: '拉取公告失败: ' + response.data['text']
          });
        } else {
          this.bulletins = response.data['data'];
        }
      }).catch(function (error) {
        
      });
      axios.get("/api/v1/rating/get", {
        params: {},
      }).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: 'error',
            message: '拉取排名失败: ' + response.data['text']
          });
        } else {
          this.ranking_top10 = response.data['data'];
        }
      }).catch(function (error) {
        
      });
      axios.get("//v1.hitokoto.cn/?c=a", {
        params: {},
      }).then((response) => {
        this.hitokoto = response.data;
      }).catch(function (error) {
        
      });
    },
    on_search_event() {
      if (this.search_input === "") {
        this.$message({
          type: 'error',
          message: "输入为空!"
        });
      } else if (this.search_select === "") {
        this.$message({
          type: 'error',
          message: "请选择搜索方式!"
        });
      } else {
        axios
            .get("/api/v1/search/problems/" + this.search_select + "/" + this.search_input, {
              params: {},
            })
            .then((response) => {
              if (response.data['code'] === 0) {
                this.search_result = response.data['data'];
              } else {
                this.$message({
                  type: "error",
                  message: "错误[" + response.data['code'] + ']: ' + response.data['text']
                });
              }
            })
            .catch(function (error) {
              
            });
      }
    },
    bulletins_check(toCheck) {
      window.location = '/#/bulletins/view?id=' + toCheck.id;
    },
    bulletins_delete(toCheck) {
      axios.post('/api/v1/bulletins/delete/' + toCheck.id).then((response) => {
        if (response.data['code'] === 0) {
          this.init();
        } else {
          this.$message({
            type: "error",
            message: "错误[" + response.data['code'] + ']: ' + response.data['text']
          });
        }
      });
    },
    bulletins_create() {
      axios.post('/api/v1/bulletins/post', {
        name: this.create_bulletin_dialog_name,
        content: this.create_bulletin_dialog_content
      }).then((response) => {
        if (response.data['code'] === 0) {
          this.create_bulletin_dialog_visible = false;
          this.init();
        } else {
          this.$message({
            type: "error",
            message: "错误[" + response.data['code'] + ']: ' + response.data['text']
          });
        }
      })
    },
    bulletins_edit(toCheck) {
      window.location = '/#/bulletins/edit?id=' + toCheck.id;
    },
    profile_click(toCheck) {
      window.location = '/#/profile?id=' + toCheck.id;
    },
    problem_click(toCheck) {
      window.location = '/#/problems/view?id=' + toCheck.id;
    },
    goto_ratings() {
      window.location = '/#/ratings';
    }
  },
  components: {
    editor: MonacoEditor,
  },
  mounted() {
    this.init();
    
  },
  data() {
    return {
      user_info: {},
      logged_in: false,
      search_input: "",
      search_select: "",
      search_result: [],
      bulletins: [],
      hitokoto: {},
      ranking_top10: [],
      create_bulletin_dialog_visible: false,
      create_bulletin_dialog_name: "",
      create_bulletin_dialog_content: "",
      app_name: this.$parent.$parent.$parent.app_name
    };
  },
};

</script>

<style scoped>

a {
  text-decoration: none;
}
</style>
