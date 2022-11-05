<template>
    <div>
        <MarkdownEditor :code="code"></MarkdownEditor>
        <div v-html="code"></div>
    </div>
</template>

<script>
import axios from "axios";
import MonacoEditor from "~/components/editor.vue";
import markdownEditor from '../components/markdown-editor.vue';


export default {
  components: { MarkdownEditor: markdownEditor },
  methods: {
    init() {
    }
  },
  data() {
    return {
      code: "nothing"
    }
  }
};
</script>

<style scoped>

</style>