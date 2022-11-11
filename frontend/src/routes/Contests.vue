<template>
  <div style="width: 90%;margin: 0 auto;">
    <el-dialog width="90%" title="创建比赛" :visible.sync="new_contest_dialog_visible">
      <span>请创建完成后于 修改比赛 处添加题目</span>
      <el-input style="margin: 10px auto;" placeholder="请输入内容" v-model="new_contest.contestName">
        <template slot="prepend">标题</template>
      </el-input>
      
      <span>比赛时间</span>
      <el-date-picker
        value-format="timestamp"
        v-model="new_contest.startTimestamp"
        type="datetimerange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期">
      </el-date-picker>

      <div style="height: 10px"></div>

      <span style="margin: 20px auto;">比赛介绍(可使用Markdown + LaTeX)</span>
      <MarkdownEditor style="margin: 10px auto;" v-model="new_contest.contestDescription"
              width="100%" height="256px"></MarkdownEditor>

      <span slot="footer" class="dialog-footer">
        <el-button @click="new_contest_dialog_visible = false">取 消</el-button>
        <el-button type="primary" @click="new_contest_on_create">确 定</el-button>
      </span>
    </el-dialog>

    <el-card shadow="hover" class="box-card">
      <div slot="header" class="clearfix">
        <span>比赛列表</span>
        <el-button v-if="logged_in && user_info['data']['other_message']['permission_level'] >= 1"
                   style="float: right; padding: 3px 0" type="text" @click="create_contest">新建比赛
        </el-button>
      </div>
      <el-table :data="contests_data" style="width: 100%" @row-click="contest_click">
        <el-table-column fixed label="发起者" width="128">
          <template v-slot="scope">
            <span>{{ scope.row.author.username }}</span>
          </template>
        </el-table-column>
        <el-table-column fixed prop="name" label="比赛名称"></el-table-column>
        <el-table-column fixed prop="formattedStartTime" label="开始时间"></el-table-column>
        <el-table-column fixed prop="formattedEndTime" label="结束时间"></el-table-column>

        <el-table-column fixed="right" label="操作" width="256">
          <template v-slot="scope">
            <el-button v-if="check_general_permission(scope.row.author_uid)" @click.native.stop="contest_edit(scope.row)" type="text"
                       size="small">修改
            </el-button>
            <el-button v-if="check_general_permission(scope.row.author_uid)" @click.native.stop="contest_remove(scope.row)" type="text"
                       size="small">删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin: 20px;"></div>
      <div style="margin: 0 auto;width: 512px;">
        <span style="font-size: 15px;">当前页号:</span>
        <el-input-number v-model="page_number" @change="handlePageNumberChange" :min="0" :max="1048576"
                         label="当前页号"></el-input-number>
        <span style="font-size: 15px;"> 最大显示: </span>
        <el-input-number v-model="contests_limit" @change="handlePageNumberChange" :min="1" :max="64"
                         label="一页显示比赛数"></el-input-number>
      </div>
      <div style="margin: 20px;"></div>
    </el-card>
  </div>
</template>

<script>
import axios from "axios";
import MonacoEditor from "~/components/editor.vue";

import utils from "../utils";
import MarkdownEditor from '../components/markdown-editor.vue';

export default {
  methods: {
    init() {
      this.page_number = this.contests_start / this.contests_limit;
      
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
      axios.get("/api/v1/contests/get/" + this.contests_start + "/" + this.contests_limit).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: 'error',
            message: '拉取比赛列表失败: ' + response.data['text']
          });
        } else {
          let contests = response.data['data'];
          for (let i = 0; i < contests.length; i++) {
            contests[i].formattedStartTime = utils.timestampToTime(contests[i].start_timestamp);
            contests[i].formattedEndTime = utils.timestampToTime(contests[i].end_timestamp);
          }
          this.contests_data = contests;
        }
      })
    },
    handlePageNumberChange() {
      window.location = '/#/contests?from=' + (this.contests_limit * this.page_number) + '&limit=' + this.contests_limit;
      this.contests_start = this.$route.query['from'] === undefined ? 0 : parseInt(this.$route.query['from']);
      this.contests_limit = this.$route.query['limit'] === undefined ? 16 : parseInt(this.$route.query['limit']);
      this.init();
    },
    contest_click(toCheck) {
      window.location = '/#/contests/view?id=' + toCheck.id;
    },
    contest_edit(toCheck) {
      window.location = '/#/contests/edit?id=' + toCheck.id;
    },
    contest_remove(toCheck) {
      axios.post('/api/v1/contests/delete/' + toCheck.id).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: 'error',
            message: '删除比赛失败: ' + response.data['text']
          });
        } else {
          this.init();
        }
      })
    },
    create_contest() {
      this.new_contest_dialog_visible = true;
    },
    new_contest_on_create() {
      this.new_contest.endTimestamp = this.new_contest.startTimestamp[1];
      this.new_contest.startTimestamp = this.new_contest.startTimestamp[0];

      this.new_contest.startTimestamp = this.new_contest.startTimestamp / 1000;
      this.new_contest.endTimestamp = this.new_contest.endTimestamp / 1000;

      axios.post('/api/v1/contests/create', this.new_contest).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: 'error',
            message: '创建比赛失败: ' + response.data['text']
          });
        } else {
          this.new_contest_dialog_visible = false;
          this.init();
        }
      })
    },
    check_general_permission(compare) {
      if (this.logged_in) {
        return this.user_info['data']['id'] === compare;
      } else {
        return false;
      }
    }
  },
  components: {
    editor: MonacoEditor,
    MarkdownEditor: MarkdownEditor,
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      contests_data: [],
      contests_start: this.$route.query['from'] === undefined ? 0 : parseInt(this.$route.query['from']),
      contests_limit: this.$route.query['limit'] === undefined ? 16 : parseInt(this.$route.query['limit']),
      new_contest_dialog_visible: false,
      new_contest: {
        contestName: "",
        contestDescription: "",
        startTimestamp: [Date.now(), Date.now()],
        endTimestamp: 0,
        problems: []
      },
      page_number: 0,
    }
  }
  ,
  mounted() {
    this.init();
  }
}
;
</script>

<style scoped>

</style>