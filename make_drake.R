library(tidyverse)
library(feather)
library(drake)


load_jobs_data <- function() {
  read_feather('data/jobs_small.feather') %>% 
      filter(year %in% c(2018, 2020)) %>% 
      filter(lang=='no') %>% 
      filter(label!= 'Lønnet arbeid i private husholdninger') %>% 
      filter(label!='Internasjonale organisasjoner og organer') %>% 
      mutate(avg_pferd = 1000*num_pferd/num_words,
             avg_itferd = 1000*num_itferd/num_words)
}



plan <- drake_plan(
  jobs = load_jobs_data(),
  report = rmarkdown::render(
    knitr_in("article.Rmd"),
    output_file = file_out("article.html")
  )
)

# lock_envir=FALSE is not recommended, but needed because of some gt() funnybusiness.
make(plan, lock_envir = FALSE)

# 
# 
# jobs %>% 
#   group_by(year_y, label) %>% 
#   summarize(avg_pferd = mean(num_pferd)) %>%
#   ggplot(aes(year_y, avg_pferd)) +
#   geom_bar(stat = 'summary', fun.y='mean') +
#   facet_wrap(vars(label))
# 
# 
# 
# # jobs
#   group_by(year_y, label) %>% 
#   summarize(avg_pferd = log(mean(num_pferd))) %>% 
#   pivot_wider( names_from = year_y, values_from=avg_pferd) -> tpairs
# 
# wilcox.test(x=tpairs[['2018']], y=tpairs[['2020']], paired = TRUE, alternative = "greater")
# 
# 
# 
# jobs_length %>% 
#   filter(year_y %in% c(2018, 2020)) %>% 
#   filter(label!= 'Lønnet arbeid i private husholdninger') %>% 
#   filter(lang=='no') %>% 
#   group_by(year_y, label) %>% 
#   
# 
# 
# 
# jobs %>% 
#   mutate(num_words = length(strsplit(description, " ")) ) %>% 
#   mutate(avg_pferd = 1000*num_pferd/num_words) -> jobs_length
# 
# 
# jobs_length %>% 
#   group_by(year_y, label) %>% 
#   
# 
# jobs_length %>% 
#   filter(year_y %in% c(2018, 2020) && lang=='no') %>% 
#   group_by(year_y, label) %>% 
#   summarize(avg_pferd = 10*mean(avg_pferd),
#             n_ads = n()) %>%
#   ggplot(aes(year_y, avg_pferd, fill=n_ads)) +
#   geom_bar(stat = 'summary', fun.y='mean') +
#   facet_wrap(vars(label))
