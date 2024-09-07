"""
Compacts Comsol models in the working directory.

Loads each Comsol model (`.mph` file) in the current folder, removes
solution and mesh data, resets the modeling history, then saves the
model file under its original name, effectively compacting its size.
"""

########################################
# Dependencies                         #
########################################
import sys
sys.path.append('../../')
import mph
import numpy as np
import yaml
import argparse
import os
import sim_util

########################################
# Main                                 #
########################################

# Display welcome message.
print('Compacting Comsol models in the current folder.')

# Start Comsol client.
print('Running Comsol client on single processor core.')


client = mph.start(cores=1)
# {'Lambda': '1[W/(K*m)]', 'p': '1000[kg/m^3]', 'c': '2000[J/(kg*K)]',
# 'sizez': '10[mm]', 'px': '5[mm]', 'py': '5[mm]',
# 'sizex': '10[mm]', 'sizey': '10[mm]',
# 'T1': '313.15[K]', 'T0': '293.15[K]',
# 'time': '60'}


class parameter_control():

    def __init__(self):
        # self.Lambda = list(np.linspace(2, 200, 20))
        self.Lambda = [0.1,0.5,1,10,20,50,100]
        self.p = [8000]
        self.c = [400]
        # self.px = list(np.linspace(-20, +20, 10))
        # self.py = list(np.linspace(-20, +20, 10))

        self.px = [0]
        self.py = [0]

        self.sizex = [10]
        self.sizey = [10]
        self.sizez = [10]

        # self.T1 = list(np.linspace(degree_K(), 300, 50))
        # self.T0 = list(np.linspace(0, 300, 50))

        self.T1 = [sim_util.degree_K(15)]
        self.T0 = [sim_util.degree_K(25)]

        # self.time = list(np.linspace(5, 40, 10))
        self.time = [5]

    def generate_series(self):
        series = []
        for i2 in range(self.p.__len__()):
            for i3 in range(self.c.__len__()):
                for i1 in range(self.Lambda.__len__()):
                    temp = {}
                    temp['Lambda'] = self.Lambda[i1]
                    temp['p'] = self.p[i2]
                    temp['c'] = self.c[i3]
            series.append(temp)
        return series


def create_folder(name, num_min, num_max, path):
    timer = sim_util.Timer()
    num = num_min
    num2 = num_max
    full_path = path

    if not os.path.exists(full_path+ '/'+name[0:name.find('.')]):
        os.makedirs(full_path+ '/'+name[0:name.find('.')])
        print(f"Folder created at: {full_path+ '/'+name[0:name.find('.')]}")
    else:
        print(f"Folder already exists at: {full_path+ '/'+name[0:name.find('.')]}")

    full_path = full_path+'/'+name[0:name.find('.')]
    param = parameter_control()
    print(f'{name}:')
    timer.start('Loading')
    try:
        model = client.load(name)
        timer.stop()
    except Exception:
        timer.cancel('Failed.')

    print(client.names())
    # print(model.parameters())
    # print(model.materials())
    # print(model.physics())
    print(model.studies())
    print(model.geometries())
    # print(model.mesh())

    series = param.generate_series()

    assert num2 <= series.__len__() or num2 == -1
    if num2 == -1:
        num2 = series.__len__()

    for i in range(num, num2, 1):
        s1 = 'Lambda'
        s2 = 'p'
        s3 = 'c'
        print(f'{sim_util.X_2(series[i][s1])}[W/(K*m)]')
        print(f'{series[i][s2]}[kg/m^3]')
        print(f'{series[i][s3]}[J/(kg*K)]')

        timer.start(f'Computing{num}')

        model.parameter('Lambda', f'{sim_util.X_2(series[i][s1])}[W/(K*m)]')
        model.parameter('p', f'{series[i][s2]}[kg/m^3]')
        model.parameter('c', f'{series[i][s3]}[J/(kg*K)]')

        model.solve()
        timer.stop()

        timer.start('Saving')

        log_name = f"{num}"
        model.export('vid', f'{full_path}/{log_name}_video.gif')
        model.export('csv_data', f'{full_path}/{log_name}_mph.txt')

        # Define your parameters
        parameters_yaml = {
            'mph_name': name,
            'Lambda': float(sim_util.X_2(series[i][s1])),
            'p': float(series[i][s2]),
            'c': float(series[i][s3]),
            'px': 0,
            'py': 0,
            'sizex': 0,
            'sizey': 0,
            'sizez': 0,
            'T1': sim_util.degree_K(40),
            'T0': sim_util.degree_K(20),
            'time': 5
        }
        # Serialize the parameters into a YAML string
        yaml_str = yaml.dump(parameters_yaml)

        # Save the YAML string to a file
        file = open(f'{full_path}/{log_name}_parameters.yaml', 'w')
        file.write(yaml_str)
        file.close()
        timer.stop()

        # Open the YAML file in read mode and load the parameters
        file = open(f'{full_path}/{log_name}_parameters.yaml', 'r')
        loaded_parameters = yaml.safe_load(file)
        print(loaded_parameters)
        file.close()

        num = num + 1

    model.save()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Create a folder with a name based on two numbers.")
    parser.add_argument("--mph", type=str, default= 'None.mph', help="The first number")
    parser.add_argument("--min", type=int, default= 0, help="The first number")
    parser.add_argument("--max", type=int, default= -1, help="The second number")
    parser.add_argument("--path", type=str, default= './output', help="The path where the folder will be created")

    args = parser.parse_args()

    create_folder(args.mph, args.min, args.max, args.path)
