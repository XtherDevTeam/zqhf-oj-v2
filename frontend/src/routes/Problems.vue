<template>
  <div style="width: 90%;margin: 0 auto;">
    <el-dialog width="50%" title="创建题目" :visible.sync="new_problem_dialog_visible">
      <span>新增题目样例请创建题目后修改</span>
      <el-input style="margin: 10px auto;" placeholder="请输入内容" v-model="new_problem_name">
        <template slot="prepend">标题</template>
      </el-input>
      <el-input style="margin: 10px auto;" placeholder="1000" v-model="new_problem_timeout">
        <template slot="prepend">超时限制</template>
      </el-input>
      <el-input style="margin: 10px auto;" placeholder="1000" v-model="new_problem_memory_limit">
        <template slot="prepend">空间限制</template>
      </el-input>
      <span style="margin: 20px auto;">题目介绍(可使用Markdown + KaTeX)</span>
      <editor style="margin: 10px auto;" v-model="new_problem_description" language="markdown"

              width="100%" height="256px"></editor>

      <el-tag :key="tag" v-for="tag in new_problem_tags" closable :disable-transitions="false" style="margin: 0 5px;"
              @close="new_problem_tags_remove(tag)">
        {{ tag }}
      </el-tag>
      <el-input class="input-new-tag" v-if="new_problem_temp_tag_visible" v-model="new_problem_temp_tag_name"
                ref="saveTagInput" size="small" @keyup.enter.native="handleTagInputConfirm"
                @blur="handleTagInputConfirm" style="width: 256px;"
      >
      </el-input>
      <el-button v-else class="button-new-tag" size="small" @click="new_problem_tag_visible_f">+ 新标签</el-button>

      <span slot="footer" class="dialog-footer">
        <el-button @click="new_problem_dialog_visible = false">取 消</el-button>
        <el-button type="primary" @click="new_problem_on_create">确 定</el-button>
      </span>
    </el-dialog>

    <el-card shadow="hover" class="box-card">
      <div slot="header" class="clearfix">
        <span>题库</span>
        <el-button v-if="logged_in && user_info['data']['other_message']['permission_level']"
                   style="float: right; padding: 3px 0" type="text" @click="new_problem">新建题目
        </el-button>
      </div>
      <el-table :data="problems_data" style="width: 100%">
        <el-table-column fixed prop="author" label="上传者" width="128"></el-table-column>
        <el-table-column fixed prop="name" label="题目名"></el-table-column>
        <el-table-column fixed v-slot="scope" label="标签">
          <el-tag :key="tag" v-for="tag in scope.row.tags" style="margin: 0 2px;">{{ tag }}</el-tag>
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="256">
          <template v-slot="scope">
            <el-button @click="problem_click(scope.row)" type="text" size="small">查看</el-button>
            <el-button v-if="check_general_permission(scope.row.author)" @click="problem_edit(scope.row)" type="text"
                       size="small">修改
            </el-button>
            <el-button v-if="check_general_permission(scope.row.author)" @click="problem_remove(scope.row)" type="text"
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
        <el-input-number v-model="problems_limit" @change="handlePageNumberChange" :min="1" :max="64"
                         label="一页显示题目数"></el-input-number>
      </div>
      <div style="margin: 20px;"></div>
    </el-card>
  </div>
</template>

<script>
import axios from "axios";
import MonacoEditor from "../components/editor.vue";


export default {
  methods: {
    init() {
      this.page_number = this.problems_start / this.problems_limit;
      
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
      axios.get("/api/v1/problems/get/" + this.problems_start + "/" + this.problems_limit).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: 'error',
            message: '拉取题目列表失败: ' + response.data['text']
          });
        } else {
          this.problems_data = response.data['data'];
          for (let problemsDataKey in this.problems_data) {
            
            this.problems_data[problemsDataKey]['tags'] = JSON.parse(this.problems_data[problemsDataKey]['tags']);
          }
        }
      })
    },
    handleTagInputConfirm() {
      let inputValue = this.new_problem_temp_tag_name;
      if (inputValue) {
        this.new_problem_tags.push(inputValue);
      }
      this.new_problem_temp_tag_visible = false;
      this.new_problem_temp_tag_name = '';
    },
    handlePageNumberChange() {
      window.location = '/#/problems?from=' + (this.problems_limit * this.page_number) + '&limit=' + this.problems_limit;
      this.problems_start = this.$route.query['from'] === undefined ? 0 : parseInt(this.$route.query['from']);
      this.problems_limit = this.$route.query['limit'] === undefined ? 16 : parseInt(this.$route.query['limit']);
      this.init();
    },
    new_problem_tags_remove(tag) {
      this.new_problem_tags.splice(this.new_problem_tags.indexOf(tag), 1);
    },
    new_problem_tag_visible_f() {
      this.new_problem_temp_tag_visible = true;
      this.$nextTick(_ => {
        this.$refs.saveTagInput.$refs.input.focus();
      });
    },

    problem_click(toCheck) {
      window.location = '/#/problems/view?id=' + toCheck.id;
    },
    problem_edit(toCheck) {
      window.location = '/#/problems/edit?id=' + toCheck.id;
    },
    problem_remove(toCheck) {
      axios.post('/api/v1/problems/delete/' + toCheck.id).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: 'error',
            message: '删除题目失败: ' + response.data['text']
          });
        } else {
          this.init();
        }
      })
    },
    new_problem() {
      this.new_problem_dialog_visible = true;
    },
    new_problem_on_create() {
      axios.post('/api/v1/problems/post', {
        name: this.new_problem_name,
        description: this.new_problem_description,
        tags: this.new_problem_tags,
        examples: [],
        timeout: parseInt(this.new_problem_timeout),
        memory_limit: parseInt(this.new_problem_memory_limit)
      }).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: 'error',
            message: '新增题目失败: ' + response.data['text']
          });
        } else {
          this.new_problem_dialog_visible = false;
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
      problems_data: [],
      problems_start: this.$route.query['from'] === undefined ? 0 : parseInt(this.$route.query['from']),
      problems_limit: this.$route.query['limit'] === undefined ? 16 : parseInt(this.$route.query['limit']),
      new_problem_dialog_visible: false,
      new_problem_name: "",
      new_problem_description: "",
      new_problem_timeout: 1000,
      new_problem_memory_limit: 65536,
      new_problem_tags: [],
      new_problem_temp_tag_name: "",
      new_problem_temp_tag_visible: false,
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