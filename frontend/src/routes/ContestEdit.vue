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
      <MarkdownEditor
        style="margin: 10px auto"
        v-model="contest_data.contestDescription"
        width="100%"
        height="256px"
      ></MarkdownEditor>

      <problems-shower v-model="problems_content" :changable="false"></problems-shower>

      <el-button type="primary" @click="submit_changes">提交</el-button>

    </el-card>
  </div>
</template>

<script>
import axios from "axios";
import MonacoEditor from "~/components/editor.vue";
import MarkdownEditor from '../components/markdown-editor.vue';
import ProblemsShower from '../components/problems-shower.vue';

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
    MarkdownEditor: MarkdownEditor,
    ProblemsShower,
  },
  mounted() {
    this.init();
  },
};
</script>

<style scoped>
</style>