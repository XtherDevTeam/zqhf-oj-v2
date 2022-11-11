<template>
  <div
    ref="container"
    v-html="renderedContent"
    class="markdown-body"
  ></div>
</template>
  
<script>
import markdownItHighlight from "markdown-it-highlight";

const markdown = require("markdown-it")(),
  markdown_with_katex = require("@iktakahiro/markdown-it-katex");

markdown.use(markdown_with_katex);
markdown.use(markdownItHighlight);

export default {
  name: "Markdown",
  props: {
    code: {
      type: String,
      default: "",
    },
  },
  data() {
    return {
      renderedContent: "",
      themeMedia: {},
    };
  },
  created() {
    this.init();
  },
  methods: {
    init() {
      this.$nextTick(() => {
        if (this.code !== undefined) {
          this.renderedContent = markdown.render(this.code);
        }        
      });
    },
  },
  watch: {
    code(val) {
      this.renderedContent = markdown.render(val);
    },
  },
  model: {
    prop: ["code"],
    event: [],
  },
};
</script>