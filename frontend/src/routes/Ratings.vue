<template>
  <div style="width: 90%;margin: 0 auto;">
    <el-card shadow="hover" class="box-card">
      <div slot="header" class="clearfix">
        <span>Rating 排名</span>
      </div>
      <el-table :data="ratings_data" style="width: 100%" @row-click="profile_click">
        <el-table-column fixed prop="id" label="UID" width="128"></el-table-column>
        <el-table-column fixed label="用户名">
            <template v-slot="scope">
              <el-avatar :size="25" :src="'/api/v1/user/image/get/' + scope.row.id"></el-avatar>
              <span style="margin: 2px 4px;">{{ scope.row.username }}</span>
              <el-tag v-if="scope.row.other_message.permission_level == 1" style="margin-left: 5px;" type="warning">Admin</el-tag>
              <el-tag v-else-if="scope.row.other_message.permission_level == 2" style="margin-left: 5px;" type="danger">Super-admin</el-tag>
              <el-tag v-else-if="scope.row.other_message.permission_level == -1" style="margin-left: 5px;" type="info">Cheater</el-tag>
            </template>
          </el-table-column>
        <el-table-column fixed prop="introduction" label="介绍"></el-table-column>
        <el-table-column fixed prop="ac_count" label="Rating" width="128"></el-table-column>
        <el-table-column fixed prop="ranking" label="全站排名" width="128"></el-table-column>
      </el-table>

      <div style="margin: 20px;"></div>
      <div style="margin: 0 auto;width: 512px;">
        <span style="font-size: 15px;">当前页号:</span>
        <el-input-number v-model="page_number" @change="handlePageNumberChange" :min="0" :max="1048576"
                         label="当前页号"></el-input-number>
        <span style="font-size: 15px;"> 最大显示: </span>
        <el-input-number v-model="ratings_limit" @change="handlePageNumberChange" :min="1" :max="64"
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
      this.page_number = this.ratings_start / this.ratings_limit;
      
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
      axios.get("/api/v1/rating/get/" + this.ratings_start + "/" + this.ratings_limit).then((response) => {
        if (response.data['code'] !== 0) {
          this.$message({
            type: 'error',
            message: '拉取Rating排名列表失败: ' + response.data['text']
          });
        } else {
          this.ratings_data = response.data['data'];
        }
      })
    },
    handlePageNumberChange() {
      window.location = '/#/ratings?from=' + (this.ratings_limit * this.page_number) + '&limit=' + this.ratings_limit;
      this.ratings_start = this.$route.query['from'] === undefined ? 0 : parseInt(this.$route.query['from']);
      this.ratings_limit = this.$route.query['limit'] === undefined ? 16 : parseInt(this.$route.query['limit']);
      this.init();
    },
    profile_click(toCheck) {
      window.location = '/#/profile?id=' + toCheck.id;
    },
  },
  components: {
    editor: MonacoEditor,
  },
  data() {
    return {
      user_info: "",
      logged_in: "",
      app_name: this.$parent.$parent.$parent.app_name,
      ratings_data: [],
      ratings_start: this.$route.query['from'] === undefined ? 0 : parseInt(this.$route.query['from']),
      ratings_limit: this.$route.query['limit'] === undefined ? 16 : parseInt(this.$route.query['limit']),
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