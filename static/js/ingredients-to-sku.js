var vm = new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     ingredients: [],
     loading: false,
     currentIngredient: {},
     message: null,
     //COUPLED WITH BACKEND DO NOT REMOVE BELOW
     newIngredient: { 'ingredient_name': '', 'quantity':0 },
   },
   mounted: function() {},
   methods: {
       getIngredients: function(skuid){
           this.loading = true;
           this.$http.get('/api/ingredients_to_sku/'+skuid)
               .then((response) => {
                   this.ingredients = response.data;
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
       },
       getIngredient: function(ingredientid){
          for(key in this.goals){
            // console.log('here')
            if(this.goals.hasOwnProperty(key)){
            // console.log(this.goals[key].id)
              if(this.goals[key].id == goalid){
                this.currentGoal = {'id':this.goals[key].id,'goalname':this.goals[key].goalname,'user':this.goals[key].user}
                $("#editGoalModal").modal('show');
              }
            }
          }
       },
       deleteIngredient: function(skuid,ingredientid){
         this.loading = true;
         // TODO: use delimiters
         this.$http.post('/api/delete_goal/' + userid + '/'+goalid)
           .then((response) => {
             this.loading = false;
             this.getGoals(userid);
           })
           .catch((err) => {
             this.loading = false;
             console.log(err);
           })
       },
       addGoal: function(skuid,ingredientid) {
         this.newGoal.user = parseInt(userid,10)
         this.loading = true;
         this.$http.post('/api/goal/'+userid,this.newGoal)
           .then((response) => {
           $("#addGoalModal").modal('hide');
           this.loading = false;
           this.getGoals(userid);
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
       },
       updateGoal: function(skuid,ingredientid) {
         this.loading = true;
         this.$http.post('/api/update_goal/'+ userid + '/'+goalid, this.currentGoal)
           .then((response) => {
             $("#editGoalModal").modal('hide');
             this.loading = false;
             this.getGoals(userid);
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
   }
   }
   });