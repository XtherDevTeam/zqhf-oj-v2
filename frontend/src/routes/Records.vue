<template>
  <div style="width: 90%;margin: 0 auto;">
    <el-card shadow="hover" class="box-card">
      <div slot="header" class="clearfix">
        <span>评测记录</span>
      </div>
      <div>
        <span>查找记录：</span>

        <el-input style="width: 200px;" placeholder="" v-model="search.uid">
          <template slot="prepend">用户UID: </template>
        </el-input>

        <el-input style="width: 200px;" placeholder="" v-model="search.pid">
          <template slot="prepend">题目ID: </template>
        </el-input>

        <el-button icon="el-icon-search" @click="update_record_data()"></el-button>
      </div>
      <el-table :data="records_data" style="width: 100%" @row-click="problem_click">
        <el-table-column fixed prop="id" label="评测编号" width="128"></el-table-column>
        <el-table-column fixed prop="author" label="上传者UID" width="128"></el-table-column>
        <el-table-column fixed prop="problem" label="题目ID" width="128"></el-table-column>
        <el-table-column fixed prop="score" label="得分" width="128"></el-table-column>
        <el-table-column fixed label="状态">
          <template v-slot="scope">
            <el-tag v-if="scope.row.status === 'Accepted'" type="success">通过</el-tag>
            <el-tag v-else-if="scope.row.status === 'Wrong answer'" type="danger">未通过</el-tag>
            <el-tag v-else type="warning">评测中</el-tag>
          </template>
        </el-table-column>
        <el-table-column fixed prop="lang" label="使用语言"></el-table-column>
      </el-table>

      <div style="margin: 20px;"></div>
      <div style="margin: 0 auto;width: 512px;">
        <span style="font-size: 15px;">当前页号:</span>
        <el-input-number v-model="page_number" @change="handlePageNumberChange" :min="0" :max="1048576"
                         label="当前页号"></el-input-number>
        <span style="font-size: 15px;"> 最大显示: </span>
        <el-input-number v-model="records_limit" @change="handlePageNumberChange" :min="1" :max="64"
                         label="一页显示题目数"></el-input-number>
      </div>
      <div style="margin: 20px;"></div>
    </el-card>
  </div>
</template>

<script>
import axios from "axios";
import MonacoEditor from "~/components/editor.vue";


export default {
  methods: {
    init() {
      this.page_number = this.records_start / this.records_limit;
      
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

        this.update_record_data();
    },
    handlePageNumberChange() {
      window.location = `/#/records?from=${this.records_limit * this.page_number}&limit=${this.records_limit}&uid=${this.search.uid}&pid=${this.search.pid}`;
      this.records_start = this.$route.query['from'] === undefined ? 0 : parseInt(this.$route.query['from']);
      this.records_limit = this.$route.query['limit'] === undefined ? 16 : parseInt(this.$route.query['limit']);
      this.update_record_data();
    },
    problem_click(toCheck) {
      window.location = '/#/records/view?id=' + toCheck.id;
    },
    update_record_data() {
      try {
        axios.post(`/api/v1/judge/get/${this.records_start}/${this.records_limit}`,
                  {'uid': parseInt(this.search.uid), 'pid': parseInt(this.search.pid)}).then((response) => {
          if (response.data['code'] !== 0) {
            this.$message({
              type: 'error',
              message: '拉取评测数据列表失败: ' + response.data['text']
            });
          } else {
            this.records_data = response.data['data'];
            for (let record = 0; record < this.records_data.length; record++) {
              this.records_data[record]['author'] = this.records_data[record]['author']['username']
            }
          }
        })
      } catch (e) {
        this.$message({
          type: 'error',
          message: '拉取评测数据列表失败: ' + e
        });
      }
      
    }
  },
  components: {
    editor: MonacoEditor,
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      records_data: [],
      records_start: this.$route.query['from'] === undefined ? 0 : parseInt(this.$route.query['from']),
      records_limit: this.$route.query['limit'] === undefined ? 16 : parseInt(this.$route.query['limit']),
      page_number: 0,
      search: {
        uid: this.$route.query['uid'] === undefined ? "-1" : this.$route.query['uid'],
        pid: this.$route.query['pid'] === undefined ? "-1" : this.$route.query['pid'],
      }
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