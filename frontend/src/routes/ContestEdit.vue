<template>
  <div id="edit">
    <el-card shadow="hover" class="box-card">
      <div slot="header" class="clearfix">
        <span>编辑比赛</span>
      </div>
      <el-input
        style="margin: 10px auto"
        placeholder="请输入内容"
        v-model="contest_data.contestName"
      >
        <template slot="prepend">标题</template>
      </el-input>

      <span>比赛时间</span>
      <el-date-picker
        value-format="timestamp"
        v-model="contest_data.startTimestamp"
        type="datetimerange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
      >
      </el-date-picker>

      <div style="height: 10px"></div>

      <span style="margin: 20px auto">比赛介绍(可使用Markdown + LaTeX)</span>
      <editor
        style="margin: 10px auto"
        v-model="contest_data.contestDescription"
        language="markdown"
        width="100%"
        height="256px"
      ></editor>

      <el-table :data="problems_content" style="width: 100%">
        <el-table-column prop="id" fixed="right" label="题目编号" width="100px"></el-table-column>
        <el-table-column fixed prop="author" label="上传者" width="128"></el-table-column>
        <el-table-column fixed prop="name" label="题目名"></el-table-column>
        <el-table-column fixed v-slot="scope" label="标签">
          <el-tag :key="tag" v-for="tag in scope.row.tags" style="margin: 0 2px;">{{ tag }}</el-tag>
        </el-table-column>

        <el-table-column fixed="right" label="操作">
          <template v-slot="scope">
            <el-button @click="remove_problem_from_list(scope.$index)" type="text" size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

    <div style="height: 10px"></div>

    <el-input placeholder="插入题目ID" v-model="insert_problem_id" style="width: 128px;"></el-input>
    <el-button type="primary" @click="insert_problem_to_list">插入题目</el-button>

    <div style="margin: 10px auto;"></div>

    <el-button type="primary" @click="submit_changes">提交</el-button>

    </el-card>
  </div>
</template>

<script>
import axios from "axios";
import MonacoEditor from "~/components/editor.vue";

export default {
  methods: {
    init() {
      axios
        .get("/api/v1/user/details", {
          params: {},
        })
        .then((response) => {
          this.user_info = response.data;
          this.logged_in = response.data["code"] === 0;
        })
        .catch(function (error) {});

      axios
        .get("/api/v1/contests/get/" + this.$route.query["id"])
        .then((response) => {
          if (response.data["data"] == null) {
            this.$message({
              type: "error",
              message: "比赛内容拉取失败!",
            });
          } else {
            this.contest_data.contestName = response.data["data"].name;
            this.contest_data.contestDescription = response.data["data"].description;
            this.contest_data.startTimestamp = [response.data["data"].start_timestamp * 1000, response.data["data"].end_timestamp * 1000];

            this.problems_content = response.data["data"].problems;
          }
        });
    },
    submit_changes() {
      this.contest_data.problems = [];
      for (let i = 0; i < this.problems_content.length; i++) {
        this.contest_data.problems.push(this.problems_content[i]['id']);
      }

      this.contest_data.endTimestamp = this.contest_data.startTimestamp[1];
      this.contest_data.startTimestamp = this.contest_data.startTimestamp[0];

      this.contest_data.startTimestamp =
        this.contest_data.startTimestamp / 1000;
      this.contest_data.endTimestamp = this.contest_data.endTimestamp / 1000;

      console.log('wdnmdnmslwqnmgb ', this.contest_data.startTimestamp, this.contest_data.endTimestamp)

      axios
        .post("/api/v1/contests/edit/" + this.$route.query["id"], this.contest_data)
        .then((response) => {
          if (response.data["code"] !== 0) {
            this.$message({
              type: "error",
              message:
                "[" +
                response["code"] +
                "] " +
                response.data["text"] +
                " 修改比赛失败",
            });
          } else {
            this.$router.back();
          }
        });
    },
    remove_problem_from_list(idx) {
      this.problems_content.splice(idx, 1);
    },
    insert_problem_to_list() {
      if (this.insert_problem_id === "") {
        this.$message({
          type: "error",
          message: "将要插入的题目ID为空!"
        });
      }
      axios.get('/api/v1/problems/get/' + this.insert_problem_id).then((response) => {
        if (response.data['code'] === 0 && this.problems_content.indexOf(response.data['data']) === -1 && response.data['data'] !== null) {
          response.data['data'].tags = JSON.parse(response.data['data'].tags);
          this.problems_content.push(response.data['data']);
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
      contest_data: {
        contestName: "",
        contestDescription: "",
        startTimestamp: [Date.now(), Date.now()],
        endTimestamp: 0,
        problems: [],
      },
      problems_content: [],
      insert_problem_id: "",
    };
  },
  components: {
    editor: MonacoEditor,
  },
  mounted() {
    this.init();
  },
};
</script>

<style scoped>
</style>