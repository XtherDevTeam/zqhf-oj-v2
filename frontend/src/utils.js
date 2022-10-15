Date.prototype.format = function (format) {
    var date = {
        "M+": this.getMonth() + 1,
        "d+": this.getDate(),
        "h+": this.getHours(),
        "m+": this.getMinutes(),
        "s+": this.getSeconds(),
        "q+": Math.floor((this.getMonth() + 3) / 3),
        "S+": this.getMilliseconds()
    };
    if (/(y+)/i.test(format)) {
        format = format.replace(RegExp.$1, (this.getFullYear() + '').substr(4 - RegExp.$1.length));
    }
    for (var k in date) {
        if (new RegExp("(" + k + ")").test(format)) {
            format = format.replace(RegExp.$1, RegExp.$1.length == 1
                ? date[k] : ("00" + date[k]).substr(("" + date[k]).length));
        }
    }
    return format;
}

export default {
    timestampToTime(timestamp) {
        var date = new Date(timestamp * 1000);
        return date.format("yyyy/MM/dd hh:mm:ss");
    },
    timestampToTime_ex(timestamp, format) {
        var date = new Date(timestamp * 1000);
        return date.format(format);
    },
    getDuration(start, end) {
        const stime = Date.parse(new Date(start * 1000)), // 开始时间
            etime = Date.parse(new Date(end * 1000)), // 结束时间
            usedTime = etime - stime, // 两个时间戳相差的毫秒数
            days = Math.floor(usedTime / (24 * 3600 * 1000)), // 计算相差的天数
            leave1 = usedTime % (24 * 3600 * 1000), // 计算天数后剩余的毫秒数
            hours = Math.floor(leave1 / (3600 * 1000)), // 小时数
            leave2 = leave1 % (3600 * 1000), // 计算小时数后剩余的毫秒数
            minutes = Math.floor(leave2 / (60 * 1000)), // 分钟数
            leave3 = leave2 % (60 * 1000), // 计算分钟数后剩余的毫秒数
            seconds = Math.round(leave3 / 1000), // 秒数
            leave4 = leave3 % (60 * 1000), // 计算秒数后剩余的毫秒数
            minseconds = Math.round(leave4 / 1000); // 毫秒数

        var date = {
            "d+": days,
            "h+": hours,
            "m+": minutes,
            "s+": seconds,
        };

        let format = "hh:mm:ss";

        for (var k in date) {
            if (new RegExp("(" + k + ")").test(format)) {
                format = format.replace(RegExp.$1, RegExp.$1.length == 1
                    ? date[k] : ("00" + date[k]).substr(("" + date[k]).length));
            }
        }
        return format;
    },
    getAppName() {
        return "肇庆华赋在线评测系统";
    }
}