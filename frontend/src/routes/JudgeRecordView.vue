<template>
  <el-card shadow="hover" class="box-card">
    <div slot="header" class="clearfix">
      <span>评测记录 {{ record_content['id'] }} </span>
      <el-tag v-if="record_content['status'] === 'Accepted'" type="success">通过</el-tag>
      <el-tag v-else-if="record_content['status'] === 'Wrong answer'" type="danger">未通过</el-tag>
      <el-tag v-else type="warning">评测中</el-tag>
      <br>
      <span>测试得分 {{ record_content['score'] }}</span>
    </div>
    <span>题目编号 {{ record_content['problem'] }}</span><br>
    <div style="margin: 10px;"></div>
    <span>使用语言 <el-tag>{{ record_content['lang'] }}</el-tag></span><br>
    <div style="margin: 10px;"></div>
    <span>提交时间 {{ record_content['timestamp'] }}</span><br>
    <div style="margin: 10px;"></div>
    <el-table :data="record_content['points']" style="width: 100%">
      <el-table-column type="expand">
        <template v-slot="props">
          <el-form style="width: 90%;margin: 0 auto;" label-position="left" inline class="points-table-expand">
            <el-form-item label="状态">
              <span><el-tag>{{ props.row['status'] }}</el-tag></span>
            </el-form-item>
            <el-form-item label="返回值">
              <span>{{ props.row['return_code'] }}</span>
            </el-form-item>
          </el-form>

          <div style="margin: 20px;"></div>

          <div style="width: 90%;margin: 0 auto;">
            <span>标准错误(stderr)</span><br>
            <div style="margin: 10px;"></div>
            <span class="markdown-body"><pre style="padding: 10px"><code>{{ props.row['stderr'] }}</code></pre></span>
            <div style="margin: 10px;"></div>

            <span>标准输出(stdout)</span><br>
            <div style="margin: 10px;"></div>
            <span class="markdown-body"><pre style="padding: 10px"><code>{{ props.row['stdout'] }}</code></pre></span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态"></el-table-column>
      <el-table-column prop="return_code" label="返回值"></el-table-column>
    </el-table>
    <div style="margin: 10px;"></div>
    <span>提交代码: </span>
    <div style="margin: 10px;"></div>
    <div class="markdown-body">
      <pre v-if="user_info.data.other_message.permission_level == 2 || user_info['data']['id'] === record_content['author']['id']"><code v-html="rendered_code_html"></code></pre>
      <pre v-else><code>您无权限查看他人代码!</code></pre>
    </div>
  </el-card>
</template>

<script>
import axios from "axios";
import MonacoEditor from "~/components/editor.vue";
import markdownItHighlight from 'markdown-it-highlight';
import hljs from "highlight.js";

const markdown = require('markdown-it')(),
    markdown_with_katex = require('@iktakahiro/markdown-it-katex');

markdown.use(markdownItHighlight);
markdown.use(markdown_with_katex)


export default {
  methods: {
    timestampToTime(timestamp) {
      console.log('wdnmd ', timestamp);
      var date = new Date(timestamp * 1000); //时间戳为10位需*1000，时间戳为13位的话不需乘1000
      return date.format('yyyy/MM/dd hh:mm:ss');
    },
    update_status() {
      axios.get('/api/v1/judge/get/' + this.$route.query['id']).then((response) => {
        console.log(response.status);
        this.record_content = response.data['data'];
        if (this.record_content == null || response.data['code'] !== 0) {
          this.$message({
            type: "error",
            message: "评测记录内容拉取失败: " + response.data.text
          });
          clearInterval(this.interval_id);
        } else {
          if (this.record_content['status'] !== 'Judging...') {
            clearInterval(this.interval_id)
            this.record_content['timestamp'] = this.timestampToTime((this.record_content['timestamp'] / 100) | 0);
            this.rendered_code_html = hljs.highlightAuto(this.record_content['code']).value;
          }
        }
      }).catch(() => {
        clearInterval(this.interval_id);
      });
    },
    init() {
      
      axios.get("/api/v1/user/details", {
        params: {},
      }).then((response) => {
        this.user_info = response.data;
        this.logged_in = response.data['code'] === 0;
      }).catch(() => {
        
      });
    },

  },
  mounted() {
    this.init();
    this.update_status();
    this.interval_id = setInterval(this.update_status, 1000);
  },
  data() {
    return {
      user_info: {},
      logged_in: "",
      record_content: {},
      interval_id: 0,
      rendered_code_html: ""
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