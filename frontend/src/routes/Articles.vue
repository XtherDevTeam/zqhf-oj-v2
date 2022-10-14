<template>
  <div style="width: 90%;margin: 0 auto;">
    <el-dialog width="50%" title="新建文章" :visible.sync="new_article_dialog_visible">
      <el-input placeholder="请输入内容" v-model="new_article_name">
        <template slot="prepend">标题</template>
      </el-input>
      <div style="margin: 20px auto;"></div>
      <span style="font-size: 14px;"><h3>内容</h3></span>
      <editor style="margin: 10px auto;" v-model="new_article_text" language="markdown"
              width="100%" height="256px"></editor>

      <el-switch
          v-model="new_article_visible"
          active-text="对所有人可见"
          inactive-text="仅自己可见">
      </el-switch>

      <span slot="footer" class="dialog-footer">
        <el-button @click="new_article_dialog_visible = false">取 消</el-button>
        <el-button type="primary" @click="new_article_on_create">确 定</el-button>
      </span>
    </el-dialog>

    <el-card shadow="hover" class="box-card">
      <div slot="header" class="clearfix">
        <span>文章列表</span>
        <el-button v-if="logged_in && user_info['data']['other_message']['permission_level'] >= 0"
                   style="float: right; padding: 3px 0" type="text" @click="new_article_dialog_visible = true;">
          新建文章
        </el-button>
      </div>
      <el-radio v-model="show_article_mode" label="all" @change="init()">展示全部</el-radio>
      <el-radio v-model="show_article_mode" label="mine" @change="init()">仅展示自己</el-radio>
      <div style="height: 20px;"></div>
      <div style="width: 100%">
        <el-input placeholder="请输入内容" v-model="search_article_content" class="input-with-select">
          <el-select style="width: 150px;" v-model="search_article_mode" slot="prepend" placeholder="查找方式">
            <el-option label="通过内容查找" value="by_text"></el-option>
            <el-option label="通过标题查找" value="by_name"></el-option>
            <el-option label="通过作者查找" value="by_author"></el-option>
          </el-select>
          <el-button slot="append" icon="el-icon-search" @click="on_search_event"></el-button>
        </el-input>
      </div>
      <el-table :data="lists_data" style="width: 100%" @row-click="article_click">
        <el-table-column fixed prop="id" label="ID" width="128"></el-table-column>
        <el-table-column fixed label="作者" width="128">
          <template v-slot="scope">
            <span>{{ scope.row.author['username'] }}</span>
          </template>
        </el-table-column>
        <el-table-column fixed prop="name" label="标题"></el-table-column>
        <el-table-column fixed="right" label="操作" width="256">
          <template v-slot="scope">
            <el-button v-if="check_general_permission(scope.row.author.username)" @click.native.stop="article_edit(scope.row)"
                       type="text" size="small">修改
            </el-button>
            <el-button v-if="check_general_permission(scope.row.author.username)"
                       @click.native.stop="article_remove(scope.row)"
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
      axios.get("/api/v1/articles/get/" + (this.show_article_mode === "all" ? "" : "my/") + this.records_start + "/" + this.records_limit).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: 'error',
            message: '拉取文章列表失败: ' + response.data['text']
          });
        } else {
          this.lists_data = response.data['data'];
        }
      })
    },
    handlePageNumberChange() {
      window.location = '/#/articles?from=' + (this.records_limit * this.page_number) + '&limit=' + this.records_limit;
      this.records_start = this.$route.query['from'] === undefined ? 0 : parseInt(this.$route.query['from']);
      this.records_limit = this.$route.query['limit'] === undefined ? 16 : parseInt(this.$route.query['limit']);
      this.init();
    },
    article_click(toCheck) {
      window.location = '/#/articles/view?id=' + toCheck.id;
    },
    new_article_on_create() {
      axios.post('/api/v1/articles/post', {
        name: this.new_article_name,
        text: this.new_article_text,
        visible: this.new_article_visible,
      }).then((response) => {
        if (response.data['code'] === 0) {
          this.$message({
            type: "success",
            message: "文章创建成功!"
          });
          this.new_article_dialog_visible = false;
          this.init();
        } else {
          this.$message({
            type: "error",
            message: "[" + response.data['code'] + "] " + response.data['text'] + " 新建文章失败!"
          });
          this.new_article_dialog_visible = false;
        }
      })
    },
    article_edit(toCheck) {
      window.location = '/#/articles/edit?id=' + toCheck.id;
    },
    article_remove(toCheck) {
      axios.post('/api/v1/articles/delete/' + toCheck.id).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: 'error',
            message: '删除失败: ' + response.data['text']
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
      if (this.search_article_content === "") {
        this.init();
      } else {
        this.show_article_mode = "all";
        axios.get('/api/v1/search/articles/' + this.search_article_mode + '/' + this.search_article_content)
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
    editor: MonacoEditor,
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      app_name: this.$parent.$parent.$parent.app_name,
      lists_data: [],
      records_start: this.$route.query['from'] === undefined ? 0 : parseInt(this.$route.query['from']),
      records_limit: this.$route.query['limit'] === undefined ? 16 : parseInt(this.$route.query['limit']),
      page_number: 0,
      new_article_dialog_visible: false,
      new_article_name: "",
      new_article_text: "",
      new_article_visible: true,
      search_article_mode: "",
      search_article_content: "",
      show_article_mode: "all",
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