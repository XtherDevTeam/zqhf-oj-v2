<template>
  <el-card shadow="hover" class="box-card">
    <div slot="header" class="clearfix">
      <span>编辑题单</span>
    </div>
    <el-input placeholder="请输入内容" v-model="problem_list_name">
      <template slot="prepend">标题</template>
    </el-input>
    <div style="margin: 10px auto;"></div>
    <span style="margin: 10px auto;">题单介绍</span>
    <editor style="margin: 10px auto;" v-model="problem_list_description" @init="editorInit" lang="markdown"
            theme="chrome"
            width="100%" height="256px"></editor>
    <div style="margin: 10px auto;"></div>

    <el-table :data="problem_list_content" style="width: 100%">
      <el-table-column prop="id" fixed="right" label="题目编号" width="100px"></el-table-column>
      <el-table-column prop="name" fixed="right" label="题目标题"></el-table-column>

      <el-table-column fixed="right" label="操作">
        <template v-slot="scope">
          <el-button @click="remove_problem_from_list(scope.$index)" type="text" size="small">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-input placeholder="插入题目ID" v-model="insert_problem_id" style="width: 128px;"></el-input>
    <el-button type="primary" @click="insert_problem_to_list">插入题目</el-button>

    <div style="margin: 10px auto;"></div>

    <el-button type="primary" @click="submit_changes">提交</el-button>
  </el-card>
</template>

<script>
import axios from "axios";

export default {
  methods: {
    init() {
      console.log(this.user_info);
      axios.get("/api/v1/user/details", {
        params: {},
      }).then((response) => {
        this.user_info = response.data;
        this.logged_in = response.data['code'] === 0;
      }).catch(function (error) {
        console.log(error);
      });

      axios.get('/api/v1/problem_lists/get/' + this.$route.query['id']).then((response) => {
        if (response.data['data'] == null) {
          this.$message({
            type: "error",
            message: "题单内容拉取失败!"
          });
        } else {
          this.problem_list_name = response.data['data']['name'];
          this.problem_list_description = response.data['data']['description'];
          this.problem_list_content = response.data['data']['problems']
        }
      });
    },
    editorInit() {
      require('brace/ext/language_tools') //language extension prerequisite...
      require('brace/mode/html')
      require('brace/mode/javascript')    //language
      require('brace/mode/less')
      require('brace/theme/chrome')
      require('brace/snippets/javascript') //snippet
    },
    submit_changes() {
      let problems_list = [];
      for (let i = 0; i < this.problem_list_content.length; i++) {
        problems_list.push(this.problem_list_content[i]['id']);
      }
      console.log(problems_list, "fuck!");
      axios.post('/api/v1/problem_lists/edit/' + this.$route.query['id'], {
        name: this.problem_list_name,
        description: this.problem_list_description,
        problems: problems_list
      }).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: "error",
            message: "[" + response.data['code'] + "] " + response.data['text'] + " 上传题单失败"
          });
        } else {
          window.location = '/#/lists';
        }
      })
    },
    remove_problem_from_list(idx) {
      this.problem_list_content.splice(idx, 1);
    },
    insert_problem_to_list() {
      if (this.insert_problem_id === "") {
        this.$message({
          type: "error",
          message: "将要插入的题目ID为空!"
        });
      }
      axios.get('/api/v1/problems/get/' + this.insert_problem_id).then((response) => {
        if (response.data['code'] === 0 && this.problem_list_content.indexOf(response.data['data']) === -1 && response.data['data'] !== null) {
          this.problem_list_content.push(response.data['data']);
          this.insert_problem_id = "";
        } else {
          this.$message({
            type: "error",
            message: "插入题目失败!"
          });
        }
      })
    }
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      edit_content: "",
      problem_list_name: "",
      problem_list_description: "",
      problem_list_content: "",
      insert_problem_id: ""
    }
  },
  components: {
    editor: require('vue2-ace-editor'),
  },
  mounted() {
    this.init();
  }
};
</script>

<style scoped>

</style>