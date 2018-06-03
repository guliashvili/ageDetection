import os


def get_images(dir):
    dir = os.path.expanduser(dir)
    files = (os.path.join(dir, file) for file in os.listdir(dir))
    files = [file for file in files if os.path.isfile(file) and not file.endswith('.txt') and '.' in file]

    return files


def gen_lst_for_bin(dir, clas):
    images = get_images(dir)
    with open(os.path.join(dir, 'lst.lst'), 'w+') as f:
        for image in images:
            name = os.path.basename(image)
            age, gender, num = name.split('_')

            if clas == 'age':
                f.write(num + ' ' + age + ' ' + name)
            else:
                f.write(num + ' ' + gender + ' ' + name)
