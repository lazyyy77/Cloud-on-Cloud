<template>
  <div>
    <el-button type="primary" @click="getMessage1">button1</el-button>
    <br>
    <li>/test {{ msg1 }}</li>
    <br>
    <el-button type="primary" @click="getMessage2">button2</el-button>
    <li>/about/test {{ msg2 }}</li>
    <br>
    <el-button type="primary" @click="getMessage3">button3</el-button>
    <li>http://localhost/about/test {{ msg3 }}</li>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'page2',
  data() {
    return {
      msg1: 'init',
      msg2: 'init',
      msg3: 'init'
    };
  },
  methods: {
    getMessage1() {
      // const path = '/bsrlb';
      axios.get('/test')
        .then((res) => {
          console.log("get");
          this.msg1 = res.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    getMessage2() {
      // const path = '/bsrlb';
      axios.get('/about/test')
        .then((res) => {
          console.log("get");
          this.msg2 = res.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    getMessage3() {
      // const path = '/bsrlb';
      axios.get('http://localhost/about/test')
        .then((res) => {
          console.log("get");
          this.msg2 = res.data;
        })
        .catch((error) => {
          console.error(error);
        });
    }
  }
}
</script>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>
