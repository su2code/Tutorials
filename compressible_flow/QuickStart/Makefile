## \file Makefile
#  \brief Makefile for the QuickStart tutorial
#  \author F. Poli
#  \version 7.5.1 "Blackbird"
#
# SU2 Project Website: https://su2code.github.io
#
# The SU2 Project is maintained by the SU2 Foundation
# (http://su2foundation.org)
#
# Copyright 2023, SU2 Contributors (cf. AUTHORS.md)
#
# SU2 is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# SU2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with SU2. If not, see <http://www.gnu.org/licenses/>.

TIME=/usr/bin/time

all: restart_flow.dat NACA0012_coef_pres.pdf NACA0012_pressure_field.png \
     adj/restart_adj_cd.dat dadj/restart_adj_cd.dat \
     NACA0012_surf_sens.pdf \
     NACA0012_coef_pres.png NACA0012_surf_sens.png

restart_flow.dat: inv_NACA0012.cfg mesh_NACA0012_inv.su2
	$(TIME) -o su2_cfd_time.out SU2_CFD $< | tee su2_cfd.log 

NACA0012_coef_pres.pdf: NACA0012_coef_pres.tex restart_flow.dat surface_flow.csv
	texfot -q lualatex $<

NACA0012_pressure_field.png: make_field_shots.py restart_flow.dat flow.vtu
	python3 make_field_shots.py

adj/restart_adj_cd.dat: adj/inv_adj_NACA0012.cfg mesh_NACA0012_inv.su2 \
                        restart_flow.dat
	cd adj \
	&& ln -sf ../mesh_NACA0012_inv.su2 ./mesh_NACA0012_inv.su2 \
	&& ln -sf ../restart_flow.dat ./solution_flow.dat \
	&& $(TIME) -o su2_cfd_adj_time.out \
	           SU2_CFD inv_adj_NACA0012.cfg | tee su2_cfd_adj.log

dadj/restart_adj_cd.dat: dadj/inv_dadj_NACA0012.cfg mesh_NACA0012_inv.su2 \
                         restart_flow.dat
	cd dadj \
	&& ln -sf ../mesh_NACA0012_inv.su2 ./mesh_NACA0012_inv.su2 \
	&& ln -sf ../restart_flow.dat ./solution_flow.dat \
	&& $(TIME) -o su2_cfd_ad_dadj_time.out \
	           SU2_CFD_AD inv_dadj_NACA0012.cfg | tee su2_cfd_ad_dadj.log

NACA0012_surf_sens.pdf: NACA0012_surf_sens.tex \
                        adj/restart_adj_cd.dat dadj/restart_adj_cd.dat \
                        adj/surface_adjoint.csv dadj/surface_adjoint.csv
	texfot -q lualatex $<

%.png: %.pdf
	convert -density 154x154 $< $@

.PHONY: clean
clean:
	-rm -f *.log *.aux *.out *adj/*.log *adj/*.out
	-rm -f *adj/solution_flow.dat *adj/mesh_NACA0012_inv.su2

.PHONY: distclean
distclean: clean
	-rm -f *.vtu *.csv *.dat *adj/*.csv *adj/*.dat *.png *.pdf
