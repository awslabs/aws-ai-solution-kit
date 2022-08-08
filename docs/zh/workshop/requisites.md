本动手实验如果从中国区域启动堆栈，请确认已进行了ICP备案或ICP exception，如果未进行备案，请联系顾问进行ICP备案；
参考：<https://www.amazonaws.cn/support/icp/>。

如果未进行ICP备案或ICP exception，则只能从全球区域启动。

确认lambda最大内存支持10GB，否则在部署堆栈过程中会报以下错误。  
Resource handler returned message: "'MemorySize' value failed to satisfy constraint: Member must have value less than or equal to 3008。

如果出现此问题，请使用3GB版本。