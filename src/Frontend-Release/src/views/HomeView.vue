<template>
  <main>
    <li>our cloud service!</li>
    <el-button type="primary" @click="getMessage1">button1</el-button>
    <li>反向代理 直接替换 外部域名{{ msg1 }}</li>
    <el-button type="primary" @click="getMessage2">button2</el-button>
    <li>反向代理 localhost+直接替换 {{ msg2 }}</li>
    <el-button type="primary" @click="getMessage3">button3</el-button>
    <li>外部域名 {{ msg3 }}</li>
    <el-button type="primary" @click="getMessage4">button4</el-button>
    <li>反向代理 直接替换 service名 {{ msg4 }}</li>
    <el-button type="primary" @click="getMessage5">button5</el-button>
    <li>反向代理 localhost+直接替换+后缀  service名{{ msg5 }}</li>
    <el-button type="primary" @click="getMessage6">button6</el-button>
    <li>反向代理 加挂后缀 clusterip {{ msg6 }}</li>
    <el-button type="primary" @click="getMessage7">button7</el-button>
    <li>反向代理 localhost+加挂后缀 clusterip {{ msg7 }}</li>

    <!-- <el-button type="primary" @click="getLocal1">button4</el-button>
    <li>JUST call localhost:8001/bsrlb {{ local1 }}</li>
    <el-button type="primary" @click="getLocal2">button5</el-button>
    <li>LB call localhost:8001/bsrlb {{ local2 }}</li>
    <el-button type="primary" @click="getLocal3">button6</el-button>
    <li>NP call bsvc-ip:8001/bsrnp {{ local3 }}</li>
    <el-button type="primary" @click="getLocal4">button7</el-button>
    <li>IP call clusterIP:8001/bsrip {{ local4 }}</li> -->
  </main>
</template>


<script>
import axios from 'axios';

export default {
  name: 'page1',
  data() {
    return {
      msg1: 'initail1',
      msg2: 'initial2',
      msg3: 'initial3',
      msg4: 'initial4',
      msg5: 'initial5',
      msg6: 'initial6',
      msg7: 'initial7',
      local1: 'l1',
      local2: 'l2',
      local3: 'l3',
      local4: 'l4'
    };
  },
  methods: {
    getMessage1() {
      // const path = '/bsrlb';
      axios.get('/bsrlb', {params: {param: '/page1'}})
        .then((res) => {
          this.msg1 = res.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    getMessage2() {
      // const path = 'localhost/bsrlb'; will find dns/localhost/bsrlb
      // const path = 'http://localhost:80/bsrlb'
      axios.get('http://localhost:80/bsrlb')
        .then((res) => {
          this.msg2 = res.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    getMessage3() {
      const path = 'http://a6c967e01c68e4ffab56b3d611fc6dd1-1484349623.us-east-1.elb.amazonaws.com:8001/page1';
      axios.get(path, {params: {param: '/page1'}})
        .then((res) => {
          this.msg3 = res.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    getMessage4() {
      // const path = '/bsr';
      axios.get('/bsrnp', {params: {param: '/page1'}})
        .then((res) => {
          this.msg4 = res.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    getMessage5() {
      const path = 'localhost:80/bsrnp/page1';
      axios.get(path, {params: {param: '/page1'}})
        .then((res) => {
          this.msg5 = res.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    getMessage6() {
      // const path = 'http://bsvc-ip/page1';
      axios.get('/bsrip/page1/', {params: {param: '/page1'}})
        .then((res) => {
          this.msg6 = res.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    getMessage7() {
      const path = 'localhost/bsrip/page1/';
      axios.get(path, {params: {param: '/page1'}})
        .then((res) => {
          this.msg7 = res.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    // getLocal1() {
    //   const path = 'http://localhost:80';
    //   axios.get(path, {params: {param: '/page2'}})
    //     .then((res) => {
    //       this.local1 = res.data;
    //     })
    //     .catch((error) => {
    //       console.error(error);
    //     });
    // },
    // getLocal2() {
    //   const path = 'http://localhost:8001/bsrlb';
    //   axios.get(path, {params: {param: '/page2'}})
    //     .then((res) => {
    //       this.local2 = res.data;
    //     })
    //     .catch((error) => {
    //       console.error(error);
    //     });
    // },
    // getLocal3() {
    //   const path = 'http://localhost:8001/bsrnp';
    //   axios.get(path, {params: {param: '/page2'}})
    //     .then((res) => {
    //       this.local3 = res.data;
    //     })
    //     .catch((error) => {
    //       console.error(error);
    //     });
    // },
    // getLocal4() {
    //   const path = 'http://localhost:8001/bsrip';
    //   axios.get(path, {params: {param: '/page2'}})
    //     .then((res) => {
    //       this.local4 = res.data;
    //     })
    //     .catch((error) => {
    //       console.error(error);
    //     });
    // },
  },
  // created() {
  //   this.getMessage();
  // },
};
</script>