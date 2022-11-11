<template>
  <div>
    <el-table :data="table" style="width: 100%">
      <el-table-column prop="id" fixed="right" label="题目编号" width="100px"></el-table-column>
      <el-table-column fixed prop="author" label="上传者" width="128"></el-table-column>
      <el-table-column fixed prop="name" label="题目名"></el-table-column>
      <el-table-column fixed v-slot="scope" label="标签">
        <el-tag :key="tag" v-for="tag in scope.row.tags" style="margin: 0 2px;">{{ tag }}</el-tag>
      </el-table-column>

      <el-table-column fixed="right" label="操作" v-if="changable">
        <template v-slot="scope">
          <el-button @click="remove_problem_from_list(scope.$index)" type="text" size="small">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div style="margin: 10px auto;"></div>

    <div v-if="changable">
      <el-input placeholder="插入题目ID" v-model="insert_problem_id" style="width: 128px;"></el-input>
      <el-button type="primary" @click="insert_problem_to_list">插入题目</el-button>
    </div>

    <div style="margin: 10px auto;"></div>

  </div>
</template>
    
<script>
import axios from "axios";

export default {
  name: "ProblemsShower",
  props: {
    table: {
      type: Array,
      default: [],
    },
    changable: {
      type: Boolean,
    }
  },
  data() {
    return {
      insert_problem_id: "",
    };
  },
  created() {
    this.init();
  },
  methods: {
    init() {
      this.$nextTick(() => {});
    },
    insert_problem_to_list() {
      if (this.insert_problem_id === "") {
        this.$message({
          type: "error",
          message: "将要插入的题目ID为空!"
        });
      }
      axios.get('/api/v1/problems/get/' + this.insert_problem_id).then((response) => {
        if (response.data['code'] === 0 && this.table.indexOf(response.data['data']) === -1 && response.data['data'] !== null) {
          response.data['data'].tags = JSON.parse(response.data['data'].tags);
          this.table.push(response.data['data']);
          this.insert_problem_id = "";
        } else {
          this.$message({
            type: "error",
            message: "插入题目失败!"
          });
        }
      })
    },
    remove_problem_from_list(idx) {
      this.table.splice(idx, 1);
    },
  },
  watch: {
    table(val) {
      this.table = val;
      this.$emit("change", this.table);
    },
  },
  model: {
    prop: ["table"],
    event: ["change"],
  },
};
</script>