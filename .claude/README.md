### 前端代码vibe coding使用步骤


skills存放目录如下所示：

![image-20260515173956166](C:\Users\heyue\AppData\Roaming\Typora\typora-user-images\image-20260515173956166.png)

#### 一、生成需求文档json

1、在项目下开启一个终端，并输入claude启动AI

![image-20260515174318179](C:\Users\heyue\AppData\Roaming\Typora\typora-user-images\image-20260515174318179.png)

2、输入/选择要执行的skills

![image-20260515174400241](C:\Users\heyue\AppData\Roaming\Typora\typora-user-images\image-20260515174400241.png)

3、按下箭头选择/excel-parser，按tab键，然后把需求文档绝对路径粘贴进来，enter执行，生成从需求文件中提取的json出来。

```
 /excel-parser "C:\Users\heyue\Desktop\工作相关\v2.0.1\合同额预算评审\合同额预算评审.xlsx" 
```

4、执行结束后会在output文件输出json文件

![image-20260515174855667](C:\Users\heyue\AppData\Roaming\Typora\typora-user-images\image-20260515174855667.png)

#### 二、生成业务代码

1、输入/选择要执行的skills，选择/front-code-generator ，按tab键，然后把output下json文件相对路径路径粘贴进来，再把实现准备好的接口文档绝对路径粘贴进来，enter执行，代码就生成好了。

```
/front-code-generator .claude\skills\excel-parser\output\合同额预算评审.json 
  "C:\Users\heyue\Desktop\工作相关\v2.0.1\合同额预算评审\合同额预算评审.md" 
```

