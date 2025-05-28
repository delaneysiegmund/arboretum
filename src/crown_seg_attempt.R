
library(lidR)

las <- readLAS("250423_Arboretum_hag.laz", select = "xyzinrc", 
               filter = "-drop_withheld")
las <- filter_duplicates(las)

las_normed <- normalize_height(las, tin())
las_normed <- filter_poi(las_normed, Z >= 1 & Z <= 30)

arb_chm <- rasterize_canopy(
  las_normed, 
  res = 0.5,
  pitfree(
    thresholds = c(0, 10, 20),
    max_edge = c(0, 1.5)
  )
)
plot(arb_chm)

p2 <- c(712440.04,3910137.43)
w <- matrix(1, 3, 3)
arb_smoothed <- terra::focal(arb_chm, w, fun = mean, na.rm = TRUE)

wf <- function(x){
  y <- abs(x/8)
  y[x <= 30] <- 4
  y[x > 80] <- 10
  return(y)
}

arb_ttops <- locate_trees(arb_smoothed, lmf(wf))

arb_sub <- sf::st_bbox(sf::st_buffer(sf::st_point(p2), 1000))
plot(terra::crop(arb_chm, arb_sub), col = height.colors(50))
plot(sf::st_geometry(arb_ttops), add = TRUE, pch = 3)

arb_segs = segment_trees(
  las_normed, 
  dalponte2016(arb_smoothed, arb_ttops)
)

arb_crowns <- crown_metrics(
  arb_segs, 
  func = .stdmetrics,
  geom = 'concave'
)

arb_sub1 <- sf::st_bbox(sf::st_buffer(sf::st_point(p2), 1000))
plot(terra::crop(arb_chm, arb_sub), col = height.colors(50))
plot(sf::st_geometry(arb_crowns), add = TRUE, pch = 3)
