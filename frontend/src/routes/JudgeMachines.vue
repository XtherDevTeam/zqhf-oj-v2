<template>
  <el-card shadow="hover" class="box-card">
    <div slot="header" class="clearfix">
      <span>在线评测机列表</span>
    </div>
    <el-table :data="machines" style="width: 100%">
      <el-table-column type="expand">
        <template v-slot="props">
          <el-form style="width: 90%;margin: 0 auto;" label-position="left" inline class="points-table-expand">
            <el-form-item label="CPU">
              <span><el-tag>{{ props.row['machine']['cpu'] }}</el-tag></span>
            </el-form-item>
            <el-form-item label="内存总量(MB)">
              <span><el-tag>{{ props.row['machine']['mem'] }}</el-tag></span>
            </el-form-item>
            <el-form-item label="状态">
              <span><el-tag>{{ props.row['status'] === 'free' ? '空闲' : '忙碌' }}</el-tag></span>
            </el-form-item>
            <el-form-item label="支持语言">
              <span><el-tag v-bind:key="index" v-for="i, index in props.row['judge-sever-support-language']">{{ i }}</el-tag></span>
            </el-form-item>
          </el-form>
        </template>
      </el-table-column>
      <el-table-column
        label="编号"
        type="index"
        width="50">
      </el-table-column>
      <el-table-column prop="status" label="状态">
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script>
import axios from "axios";
import markdownItHighlight from 'markdown-it-highlight';

const markdown = require('markdown-it')(),
    markdown_with_katex = require('@iktakahiro/markdown-it-katex');

markdown.use(markdownItHighlight);
markdown.use(markdown_with_katex)


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

      axios.get("/api/v1/judge/machines", {
        params: {},
      }).then((response) => {
        this.machines = response.data['data'];
        if (this.machines == null || response.data['code'] !== 0) {
          this.$message({
            type: "error",
            message: "评测机状态拉取失败!"
          });
        }
      }).catch(function (error) {
        
      });
    },

  },
  mounted() {
    this.init();
  },
  data() {
    return {
      user_info: {},
      logged_in: "",
      machines: {},
    }
  }
};
</script>

<style scoped>
.box-card {
  width: 70%;
  margin: 0 auto;
}

.points-table-expand {
  font-size: 0;
}

.points-table-expand label {
  width: 90px;
  color: #99a9bf;
}

.points-table-expand .el-form-item {
  margin-right: 0;
  margin-bottom: 0;
  width: 50%;
}
</style>