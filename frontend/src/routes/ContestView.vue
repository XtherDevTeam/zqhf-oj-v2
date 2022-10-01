<template>
  <el-card class="box-card" shadow="hover" style="width: 100%">
    <el-tabs v-model="pageName" @tab-click="handleClick">
      <el-tab-pane label="比赛介绍" name="contest-view">
        <h2 class="contest-title">欢迎来到 {{ contest_info.name }}</h2>
        <span class="contest-info">
          本次竞赛由管理员 {{ contest_info.author.username }} 发起, 时长
          {{ contest_duration }}.
        </span>

        <h3>比赛介绍</h3>
        <div
          class="markdown-body"
          id="markdownRenderedPlace"
          v-html="rendered_description"
        ></div>

        <div style="height: 20px"></div>

        <div v-if="contest_info.ended">
          <el-alert
            title="这场比赛已结束"
            :description="'由于技术原因, zqhf-oj-v2 不提供比赛复现, 您可以在 排行榜 查看您的比赛成绩.'"
            type="info"
            :closable="false"
          >
          </el-alert>
        </div>
        <div v-else-if="logged_in">
          <el-alert
            title="您已报名本次比赛"
            :description="
              '这场比赛将在 ' +
              contest_time[0] +
              ' 开始, ' +
              contest_time[1] +
              ' 结束, 请注意比赛时间.'
            "
            type="success"
            :closable="false"
            v-if="this.contest_info.joined"
          >
          </el-alert>
          <el-button v-else type="primary" @click="join">报名比赛</el-button>
        </div>
        <div v-else>
          <el-alert
            title="请登录后参加比赛！"
            type="error"
            :closable="false"
            show-icon
          >
          </el-alert>
        </div>
      </el-tab-pane>

      <el-tab-pane label="题目列表" name="problem-list">
        <el-table :data="this.contest_info.problems" style="width: 100%">
          <el-table-column prop="id" fixed="right" label="题目编号" width="100px"></el-table-column>
          <el-table-column prop="author" label="上传者" width="128"></el-table-column>
          <el-table-column prop="name" label="题目名"></el-table-column>
          <el-table-column v-slot="scope" label="标签">
            <el-tag :key="tag" v-for="tag in scope.row.tags" style="margin: 0 2px;">{{ tag }}</el-tag>
          </el-table-column>

          <el-table-column fixed="right" label="操作">
            <template v-slot="scope">
              <el-button @click="goto_problem_view(scope.$index)" type="text" size="small">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="排名榜" name="ranking"></el-tab-pane>
    </el-tabs>
  </el-card>
</template>
  
<script>
import axios from "axios";
import MonacoEditor from "../components/editor.vue";

import markdownItHighlight from "markdown-it-highlight";

import utils from "../utils";

const markdown = require("markdown-it")(),
  markdown_with_katex = require("@iktakahiro/markdown-it-katex");

markdown.use(markdown_with_katex);
markdown.use(markdownItHighlight);

export default {
  methods: {
    handleClick() {},
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
          this.contest_info = response.data["data"];
          if (this.contest_info == null) {
            this.$message({
              type: "error",
              message: "比赛内容拉取失败: " + response.data["text"],
            });
          } else {
            // format time
            this.contest_time = [
              utils.timestampToTime(this.contest_info.start_timestamp),
              utils.timestampToTime(this.contest_info.end_timestamp),
            ];

            this.contest_duration = utils.getDuration(
              this.contest_info.start_timestamp,
              this.contest_info.end_timestamp
            );

            // render html
            this.rendered_description = markdown.render(
              this.contest_info.description
            );
          }
        });
    },
    join() {
      axios
        .post("/api/v1/contests/join/" + this.$route.query["id"])
        .then((response) => {
          if (this.response.data["status"] != 0) {
            this.$message({
              type: "error",
              message: "报名失败: " + response.data["text"],
            });
          } else {
            this.init();
          }
        });
    },
    goto_problem_view(tid) {
      window.location = '/#/contests/solve?contest=' + this.$route.query["id"] + '&t=' + tid;
    }
  },
  components: {
    editor: MonacoEditor,
  },
  data() {
    return {
      pageName: "contest-view",
      user_info: {},
      logged_in: false,
      app_name: this.$parent.$parent.$parent.app_name,
      ranking_page_start: 0,
      ranking_page_end: 0,
      ranking_data: [],
      contest_info: {},
      contest_time: [],
      rendered_description: "",
      contest_duration: "",
    };
  },
  mounted() {
    this.init();
  },
};
</script>
  
  <style scoped>
</style>