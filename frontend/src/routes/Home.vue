<template>
  <el-container>
    <el-aside width="70%">
      <img src="../assets/head-image.png" style="width: 100%;"/>
      <el-card class="is-always-shadow el-card" style="height: 500px; margin: 10px auto;">
        <div slot="header" class="clearfix">
          <span>公告</span>
        </div>
        <el-table :data="bulletins" style="width: 100%">
          <el-table-column fixed prop="id" label="编号" width="64"></el-table-column>
          <el-table-column fixed prop="time" label="日期" width="200"></el-table-column>
          <el-table-column prop="name" label="名称"></el-table-column>
          <el-table-column fixed="right" label="操作" width="100">
            <template v-slot="scope">
              <el-button @click="bulletins_check(scope.row)" type="text" size="small">查看</el-button>
              <el-button v-if="logged_in && user_info['data']['permission']" type="text" size="small">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-aside>
    <el-main>
      <div v-if="logged_in === true">
        <el-card>
          <div slot="header" class="clearfix">
            <span>{{ user_info['data']['username'] }}</span>
          </div>
          <div class="text item">{{ user_info['data']['introduction'] }}</div>
          <div class="text item">已通过题目: {{ user_info['data']['ac_count'] }}</div>
        </el-card>
        <el-card style="margin: 10px auto;">
          <div slot="header" class="clearfix">
            <span>一言(ひとこと)</span>
          </div>
          <div class="text item">{{ hitokoto['hitokoto'] }}</div>
          <div class="text item">-- 《{{ hitokoto['from'] }}》 {{ hitokoto['from_who'] }}</div>
        </el-card>
        <el-card style="margin: 10px auto; height: 512px;">
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
          <el-table :data="search_result" style="width: 100%">
            <el-table-column prop="id" label="题号"></el-table-column>
            <el-table-column prop="name" label="名称"></el-table-column>
          </el-table>
        </el-card>
      </div>
      <div v-else>
        <el-card>
          <span>请先登录!</span>
        </el-card>
      </div>
    </el-main>
  </el-container>
</template>

<script>
import axios from "axios";

export default {
  methods: {
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
      axios
          .get("/api/v1/bulletins/get/0/10", {
            params: {},
          })
          .then((response) => {
            if (response.data['code'] !== 0) {
              this.$message({
                type: 'error',
                message: '拉取公告失败: ' + response.data['text']
              });
            } else {
              this.bulletins = response.data['data'];
            }
          })
          .catch(function (error) {
            console.log(error);
          });
      axios
          .get("//v1.hitokoto.cn/?c=a", {
            params: {},
          })
          .then((response) => {
              this.hitokoto = response.data;
          })
          .catch(function (error) {
            console.log(error);
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
              if (response.data['code'] == 0) {
                this.search_result = response.data['data'];
              } else {
                this.$message({
                  type: "error",
                  message: "错误[" + response.data['code'] + ']: ' + response.data['text']
                });
              }
            })
            .catch(function (error) {
              console.log(error);
            });
      }
    },
    bulletins_check(toCheck) {
      window.location = '/#/bulletins/view?id=' + toCheck.id;
    }
  },
  created() {
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
    };
  },
};

</script>

<style scoped>

a {
  text-decoration: none;
}
</style>
