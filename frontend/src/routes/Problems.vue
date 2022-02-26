<template>
  <div style="width: 90%;">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>题库</span>
        <el-button v-if="logged_in && user_info['data']['other_message']['permission_level']"
                   style="float: right; padding: 3px 0" type="text">新建题目
        </el-button>
      </div>
      <el-table :data="problems_data" style="width: 100%">
        <el-table-column fixed prop="author" label="上传者" width="128"></el-table-column>
        <el-table-column fixed prop="name" label="题目名"></el-table-column>
        <el-table-column fixed v-slot="scope" label="标签">
          <el-tag v-for="this_tag in scope.row['tags']">{{ this_tag }}</el-tag>
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="100">
          <template v-slot="scope">
            <el-button @click="problem_click(scope.row)" type="text" size="small">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
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
      axios.get("/api/v1/problems/get/" + this.problems_start + "/" + this.problems_limit).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: 'error',
            message: '拉取题目列表失败: ' + response.data['text']
          });
        } else {
          this.problems_data = response.data['data'];
          for (let problemsDataKey in this.problems_data) {
            console.log(this.problems_data[problemsDataKey]);
            this.problems_data[problemsDataKey]['tags'] = JSON.parse(this.problems_data[problemsDataKey]['tags']);
          }
        }
      })
    },
    problem_click(toCheck) {

    }
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      app_name: this.$parent.$parent.$parent.app_name,
      problems_data: [],
      problems_start: this.$route.query['from'] === undefined ? 0 : this.$route.query['from'],
      problems_limit: this.$route.query['limit'] === undefined ? 32 : this.$route.query['limit'],
    }
  },
  mounted() {
    this.init();
  }
};
</script>

<style scoped>

</style>