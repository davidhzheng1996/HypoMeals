var vm = new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     ingredients: [],
     loading: false,
     message: null,
   },
   mounted: function() {
       // this.getGoals();
   },
   methods: {
       getIngredients: function(userid,goalid){
            let api_url = '/api/calculate_goal/'+userid+'/'+goalid;
           // if(this.search_term !== '' || this.search_term !== null) {
           //      api_url = '/api/search_manufacture_goal/'+userid+'/'+goalid+this.search_term
           // }
           this.loading = true;
           this.$http.get(api_url)
               .then((response) => {
                   this.ingredients = response.data;
                   this.loading = false;
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
  
   }
   });