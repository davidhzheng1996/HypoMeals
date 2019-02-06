var vm = new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     goals: [],
     loading: false,
     currentGoal: {},
     message: null,
     search_term: '',
     // search_suggestions: search_suggestions,
     search_input: '',
     //COUPLED WITH BACKEND DO NOT REMOVE BELOW
     newGoal: { 'goal_sku_name': '', 'desired_quantity': 0, 'user': null, 'sku': null, 'name':-1},
   },
   mounted: function() {
       // this.getGoals();
   },
   methods: {
       getGoals: function(userid,goalid){
            let api_url = '/api/manufacture_goal/'+userid+'/'+goalid;
           // if(this.search_term !== '' || this.search_term !== null) {
           //      api_url = '/api/search_manufacture_goal/'+userid+'/'+goalid+this.search_term
           // }
           this.loading = true;
           this.$http.get(api_url)
               .then((response) => {
                   this.goals = response.data;
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
       },
       getGoal: function(id){
           for(key in this.goals){
            // console.log('here')
            if(this.goals.hasOwnProperty(key)){
            // console.log(this.goals[key].id)
              if(this.goals[key].id == id){
                this.currentGoal = {'id':this.goals[key].id,'goal_sku_name':this.goals[key].goal_sku_name,'user':this.goals[key].user,'desired_quantity':this.goals[key].desired_quantity,'sku':this.goals[key].sku,'name':this.goals[key].name}
                $("#editGoalModal").modal('show');
              }
            }
          }
       },
       deleteGoal: function(id){
         this.loading = true;
         // TODO: use delimiters
         this.$http.post('/api/delete_manufacture_goal/' + id )
           .then((response) => {
             this.loading = false;
             for(key in this.goals){
            // console.log('here')
              if(this.goals.hasOwnProperty(key)){
              // console.log(this.goals[key].id)
                if(this.goals[key].id == id){
                  this.goals.splice(key,1)
                }
              }
          }
           })
           .catch((err) => {
             this.loading = false;
             console.log(err);
           })
       },
       addGoal: function(userid,goalid) {
         this.newGoal.user = parseInt(userid)
         this.newGoal.name = parseInt(goalid)
         this.loading = true;
         console.log(this.newGoal)
         this.$http.post('/api/manufacture_goal/',this.newGoal)
           .then((response) => {
           $("#addGoalModal").modal('hide');
           this.loading = false;
           this.getGoals(userid,goalid);
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
       },
       exportCSV: function(){
        this.loading = true;
        // Export all current skus to a csv file
        // https://codepen.io/dimaZubkov/pen/eKGdxN
        let csvContent = "data:text/csv;charset=utf-8,";
        csvContent += [
          Object.keys(this.goals[0]).join(","),
          // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax
          ...this.goals.map(key => Object.values(key).join(","))
        ].join("\n");
        const url = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "goal.csv");
        link.click();
       },
      //  search_input_changed: function(userid, goalid) {
      //   const that = this
      //   console.log(this.search_term);
      //   this.$http.get('/api/manufacture_goal/'+userid+'/'+goalid+'/'+'?search='+this.search_term)
      //           .then((response) => {
      //                   for (let i = 0; i < response.data.length; i++) {
      //                     //console.log(response.data[i].ingredient_name);
      //                   }
      //                   this.getGoals();
      //           })
      // },
       updateGoal: function(userid,goalid) {
         this.loading = true;
         this.$http.post('/api/update_manufacture_goal/',   this.currentGoal)
           .then((response) => {
             $("#editGoalModal").modal('hide');
           this.loading = false;
           this.currentGoal = response.data;
           this.getGoals(userid,goalid);
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
   },

  
   }
   });