<template>
  <div style="width: 90%;margin: 0 auto;">
    <el-dialog width="50%" title="创建题单" :visible.sync="new_problem_list_dialog_visible">
      <span>新建题单之后编辑题单以新增题目</span>
      <el-input style="margin: 10px auto;" placeholder="请输入内容" v-model="new_problem_list_name">
        <template slot="prepend">标题</template>
      </el-input>
      <span style="margin: 20px auto;">题单介绍(可使用Markdown + KaTeX)</span>
      <editor style="margin: 10px auto;" v-model="new_problem_list_description" @init="editorInit" lang="markdown"
              theme="chrome"
              width="100%" height="256px"></editor>

      <span slot="footer" class="dialog-footer">
        <el-button @click="new_problem_list_dialog_visible = false">取 消</el-button>
        <el-button type="primary" @click="new_problem_list_on_create">确 定</el-button>
      </span>
    </el-dialog>

    <el-card shadow="hover" class="box-card">
      <div slot="header" class="clearfix">
        <span>题单列表</span>
        <el-button v-if="logged_in && user_info['data']['other_message']['permission_level']"
                   style="float: right; padding: 3px 0" type="text" @click="new_problem_list_dialog_visible = true;">
          新建题单
        </el-button>
      </div>
      <div style="width: 100%">
        <el-input placeholder="请输入内容" v-model="search_problem_list_content" class="input-with-select">
          <el-select style="width: 150px;" v-model="search_problem_list_mode" slot="prepend" placeholder="查找方式">
            <el-option label="通过描述查找" value="by_description"></el-option>
            <el-option label="通过标题查找" value="by_name"></el-option>
          </el-select>
          <el-button slot="append" icon="el-icon-search" @click="on_search_event"></el-button>
        </el-input>
      </div>
      <el-table :data="lists_data" style="width: 100%">
        <el-table-column fixed prop="id" label="题单编号" width="128"></el-table-column>
        <el-table-column fixed label="上传者" width="128">
          <template v-slot="scope">
            <span>{{ scope.row.author['username'] }}</span>
          </template>
        </el-table-column>
        <el-table-column fixed prop="name" label="标题"></el-table-column>
        <el-table-column fixed="right" label="操作" width="256">
          <template v-slot="scope">
            <el-button @click="problem_list_click(scope.row)" type="text" size="small">查看</el-button>
            <el-button v-if="check_general_permission(scope.row.author.username)" @click="problem_list_edit(scope.row)"
                       type="text" size="small">修改
            </el-button>
            <el-button v-if="check_general_permission(scope.row.author.username)"
                       @click="problem_list_remove(scope.row)"
                       type="text" size="small">删除
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
        <el-input-number v-model="records_limit" @change="handlePageNumberChange" :min="1" :max="64"
                         label="一页显示题目数"></el-input-number>
      </div>
      <div style="margin: 20px;"></div>
    </el-card>
  </div>
</template>

<script>
import axios from "axios";


export default {
  methods: {
    editorInit() {
      require('brace/ext/language_tools') //language extension prerequisite...
      require('brace/mode/html')
      require('brace/mode/javascript')    //language
      require('brace/mode/less')
      require('brace/theme/chrome')
      require('brace/snippets/javascript') //snippet
    },
    init() {
      this.page_number = this.records_start / this.records_limit;
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
      axios.get("/api/v1/problem_lists/get/" + this.records_start + "/" + this.records_limit).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: 'error',
            message: '拉取题单数据列表失败: ' + response.data['text']
          });
        } else {
          this.lists_data = response.data['data'];
        }
      })
    },
    handlePageNumberChange() {
      window.location = '/#/lists?from=' + (this.records_limit * this.page_number) + '&limit=' + this.records_limit;
      this.records_start = this.$route.query['from'] === undefined ? 0 : parseInt(this.$route.query['from']);
      this.records_limit = this.$route.query['limit'] === undefined ? 32 : parseInt(this.$route.query['limit']);
      this.init();
    },
    problem_list_click(toCheck) {
      window.location = '/#/lists/view?id=' + toCheck.id;
    },
    new_problem_list_on_create() {
      axios.post('/api/v1/problem_lists/post', {
        name: this.new_problem_list_name,
        description: this.new_problem_list_description,
        problems: [],
      }).then((response) => {
        if (response['code'] === 0) {
          this.$message({
            type: "success",
            message: "题单创建成功!"
          });
          this.init();
        } else {
          this.$message({
            type: "error",
            message: "[" + response.data['code'] + "] " + response.data['text'] + " 新建题单失败!"
          });
          this.new_problem_list_dialog_visible = false;
        }
      })
    },
    problem_list_edit(toCheck) {
      window.location = '/#/lists/edit?id=' + toCheck.id;
    },
    problem_list_remove(toCheck) {
      axios.post('/api/v1/problem_lists/delete/' + toCheck.id).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: 'error',
            message: '删除题单失败: ' + response.data['text']
          });
        } else {
          this.init();
        }
      })
    },
    check_general_permission(compare) {
      if (this.logged_in) {
        return this.user_info['data']['other_message']['permission_level'] === 1 && this.user_info['data']['username'] === compare ||
            this.user_info['data']['other_message']['permission_level'] === 2;
      } else {
        return false;
      }
    },
    on_search_event() {
      if (this.search_problem_list_content === "") {
        this.init();
      } else {
        axios.get('/api/v1/search/problem_lists/' + this.search_problem_list_mode + '/' + this.search_problem_list_content)
            .then((response) => {
              if (response.data['code'] === 0) {
                this.lists_data = response.data['data'];
              } else {
                this.$message({
                  type: 'error',
                  message: '搜索题目失败: ' + response.data['text']
                });
              }
            })
      }
    }
  },
  components: {
    editor: require('vue2-ace-editor'),
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      app_name: this.$parent.$parent.$parent.app_name,
      lists_data: [],
      records_start: this.$route.query['from'] === undefined ? 0 : parseInt(this.$route.query['from']),
      records_limit: this.$route.query['limit'] === undefined ? 32 : parseInt(this.$route.query['limit']),
      page_number: 0,
      new_problem_list_dialog_visible: false,
      new_problem_list_name: "",
      new_problem_list_description: "",
      search_problem_list_mode: "",
      search_problem_list_content: "",
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