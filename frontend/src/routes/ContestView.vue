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
        <Markdown v-model="contest_info['description']"></Markdown>

        <div style="height: 20px"></div>

        <div v-if="contest_info.ended">
          <el-alert
            title="这场比赛已结束"
            :description="'由于技术原因, zqhf-oj-v2 不提供比赛复现, 您可以在 排行榜 查看您的比赛成绩.'"
            type="info"
            show-icon
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
            show-icon
            type="success"
            :closable="false"
            v-if="this.contest_info.joined"
          >
          </el-alert>
          <div v-else>
            <el-alert
              title="您未报名本场比赛"
              :description="
                '这场比赛将在 ' +
                contest_time[0] +
                ' 开始, ' +
                contest_time[1] +
                ' 结束.'
              "
              show-icon
              type="info"
              :closable="false"
            >
            </el-alert>
            <el-button style="margin-top: 10px;" type="primary" @click="join">报名比赛</el-button>
          </div>
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
        <el-table :data="contest_info.problems" style="width: 100%" :row-class-name="generateIndex" @row-click="goto_problem_view">
          <el-table-column prop="id" fixed label="题目编号" width="100px"></el-table-column>
          <el-table-column prop="author" label="上传者" width="128"></el-table-column>
          <el-table-column prop="name" label="题目名"></el-table-column>
          <el-table-column v-slot="scope" label="标签">
            <el-tag v-for="(item, index) in scope.row.tags" :key="index" style="margin: 0 2px;">{{ item }}</el-tag>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="排名榜" name="ranking">
        <span class="contest-info">
          {{ user_info.data.username }} 的比赛情况: 总分 {{ my_ranking.final_score }} 排名 {{ my_ranking.ranking }}
          <el-button style="float: right; padding: 3px 0" type="text" @click="refresh_ranking_table()">刷新</el-button>
        </span>

        <el-table :data="ranking_data" style="width: 100%">
          <el-table-column fixed prop="ranking" label="#" width="128"></el-table-column>
          <el-table-column fixed prop="username" label="用户名" width="128"></el-table-column>
          <el-table-column fixed label="各题分数">
            <template v-slot="scope">
              <el-tag v-for="(item, index) in scope.row.scores" :key="index" style="margin: 0 2px;">{{ item }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column fixed prop="final_score" label="最终分数"></el-table-column>
        </el-table>

      <div style="margin: 20px;"></div>

      <div style="margin: 0 auto;width: 512px;">
        <span style="font-size: 15px;">当前页号: </span>
        <el-input-number v-model="ranking_page_start" @change="refresh_ranking_table" :min="0" :max="1048576"
                         label="当前页号"></el-input-number>
        <span style="font-size: 15px;"> 最大显示: </span>
        <el-input-number v-model="ranking_page_limit" @change="refresh_ranking_table" :min="1" :max="64"
                         label="一页显示排名数"></el-input-number>
      </div>

      <div style="margin: 20px;"></div>

      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>
  
<script>
import axios from "axios";
import MonacoEditor from "~/components/editor.vue";

import utils from "../utils";
import Markdown from "~/components/markdown.vue";
import ProblemsShower from '../components/problems-shower.vue';

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
          this.contest_info = response.data.data;
          if (response.data.code !== 0) {
            this.$message({
              type: "error",
              message: "比赛内容拉取失败: " + response.data.text,
            });
          } else {
            console.log(this.contest_info.description);
            // format time
            this.contest_time = [
              utils.timestampToTime(this.contest_info.start_timestamp),
              utils.timestampToTime(this.contest_info.end_timestamp),
            ];

            this.contest_duration = utils.getDuration(
              this.contest_info.start_timestamp,
              this.contest_info.end_timestamp
            );
          }
        });
    },
    join() {
      axios
        .post("/api/v1/contests/join/" + this.$route.query["id"])
        .then((response) => {
          if (response.data.code !== 0) {
            this.$message({
              type: "error",
              message: "报名失败: " + response.data["text"],
            });
          } else {
            this.init();
            this.refresh_ranking_table();
          }
        });
    },
    goto_problem_view(row) {
      if (!this.contest_info.ended) {
        window.location = '/#/contests/solve?contest=' + this.$route.query["id"] + '&t=' + row.index;
      } else {
        this.$message({
          type: 'warning',
          message: '比赛已结束，正在前往题库页面......'
        });
        window.location = '/#/problems/view?id=' + row.id;
      }
    },
    refresh_ranking_table() {
      axios
        .get("/api/v1/contests/" + this.$route.query["id"] + "/ranking", {
          params: {},
        })
        .then((response) => {
          if (response.data.code == 0) {
            this.my_ranking = response.data.data;
          } else {
            this.$message({
              type: 'error',
              message: '拉取用户排名失败: ' + response.data['text']
            });
          }
        })
        .catch(function (error) {});

        axios
        .get("/api/v1/contests/" + this.$route.query["id"] + "/ranking/" + this.ranking_page_start + "/" + this.ranking_page_limit, {
          params: {},
        })
        .then((response) => {
          if (response.data.code == 0) {
            this.ranking_data = response.data.data;
          } else {
            this.$message({
              type: 'error',
              message: '拉取排名失败: ' + response.data['text']
            });
          }
        })
        .catch(function (error) {});
    },
    generateIndex({row, rowIndex}) {
      console.log(rowIndex);
      row.index = rowIndex;
    }
  },
  components: {
    editor: MonacoEditor,
    Markdown,
  },
  data() {
    return {
      pageName: "contest-view",
      user_info: {},
      logged_in: false,
      ranking_page_start: 0,
      ranking_page_limit: 16,
      ranking_data: [],
      my_ranking: {},
      contest_info: {},
      contest_time: [],
      rendered_description: "",
      contest_duration: "",
    };
  },
  mounted() {
    this.init();
    this.refresh_ranking_table();
  },
};
</script>
  
  <style scoped>
</style>