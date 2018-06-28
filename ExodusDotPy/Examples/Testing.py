import os,sys
sys.path.append(r"/projects/seacas/linux/current/lib")
import numpy as np
import exodus
from matplotlib import pyplot as plt
FPATH=(r'/gpfs1/jchewso/MethaneOldFlame_Coflow'+ 
       r'/OldFlame_1m_CH4_SMAGcoflow-C01_mixFrac_Test24'+ 
       r'/solution_LES/')
FNAME=r'lines_at_p3.e'
data=exodus.exodus(FPATH+FNAME,array_type='numpy')
try:
    """check the exodus file contents """

    print "Exodus file has title:", data.title()
    print "Exodus file has", data.num_dimensions(), "dimensions"
    print "Exodus file has", data.num_nodes(), "nodes"
    print "Exodus file has", data.num_elems(), "elements"
    print "Exodus file has", data.num_blks(), "blocks"
    print "Exodus file has", data.num_node_sets(), "node sets"
    print "Exodus file has", data.num_times(), "time steps"
    
    # get time and block ids
    times_whole = data.get_times()
    blocks = data.get_elem_blk_ids()
    
    # print block id
    print "Block id"
    blocks = data.get_elem_blk_ids()
    for block in blocks:
        print "\tblock id = ", block
        
    # get coordinates
    coordinates = data.get_coords()
    print "Local Node Id 1 has coordinates:", coordinates[0][0], coordinates[1][0], coordinates[2][0]
    nn = (data.num_nodes() - 1)
    print "Local Node Id", data.num_nodes(), "has coordinates:", coordinates[0][nn], coordinates[1][nn], coordinates[2][nn] 
        
    # print variable names
    print "Nodal Variable Names"
    nodeVarNames = data.get_node_variable_names()
    for name in nodeVarNames:
        print "\t" + name
        
    # create numpy arrays to store data.
    # since we are taking statistics we need only look at the data once the plume is fully developed
    time_start = 10
    time_indices = np.where(times_whole > time_start)[0]
    time_size = time_indices.size
    times = times_whole[time_indices]
    mfrac = np.zeros((time_size, coordinates[0].size))
    xvel = np.zeros((time_size, coordinates[0].size))
    yvel = np.zeros((time_size, coordinates[0].size))
    zvel = np.zeros((time_size, coordinates[0].size))
    
    # get data and store in numpy arrays
    for i, time_step in enumerate(time_indices):
        t = times_whole[time_step]
        #print("Processing data: Time {}, Time Step {}".format(t, time_step+1))
        mfrac[i] = data.get_node_variable_values("mixture_fraction",time_step+1)
        xvel[i] = data.get_node_variable_values("x_vel",time_step+1)
        yvel[i] = data.get_node_variable_values("y_vel",time_step+1)
        zvel[i] = data.get_node_variable_values("z_vel",time_step+1)

    # close file
    data.close()

except:
    #close file
    print "Unexpected error:"
    data.close()
    
# save coordinates in variable x
x = coordinates
print "Coordinates shape",len(x[0])
plt.plot(x[0],x[1],'-o')
plt.show()

angle=np.arctan2(x[1],x[0]+1e-12)
plt.plot(x[0]**2+x[1]**2,angle,'-o')
plt.show()
