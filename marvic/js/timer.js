function startTimer(closeTime){

    let end=new Date()
    
    let parts=closeTime.split(":")
    
    end.setHours(parts[0])
    end.setMinutes(parts[1])
    end.setSeconds(0)
    
    setInterval(function(){
    
    let now=new Date()
    
    let diff=end-now
    
    let h=Math.floor(diff/1000/60/60)
    let m=Math.floor(diff/1000/60)%60
    let s=Math.floor(diff/1000)%60
    
    document.getElementById("timer").innerHTML =
    "Submission closes in: "+h+"h "+m+"m "+s+"s"
    
    },1000)
    
    }
    