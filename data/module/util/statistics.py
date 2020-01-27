def build_cohen_kappa_matrix(map1, map2):

    matrix = []
    subject_index_map = {}
    next_index_map = {'value': 0}

    def check_subject(to_check):
        if to_check not in subject_index_map:
            # is a new matrix subject
            subject_index_map[to_check] = next_index_map['value']
            next_index_map['value'] += 1

            # expanding matrix
            for i in range(0, len(matrix)):
                matrix[i].append(0)

            matrix.append([0] * (len(matrix) + 1))

    for key, subject in map1.items():

        if key in map2:

            check_subject(subject)
            subject_index = subject_index_map[subject]
            if map2[key] == subject:  # agreement
                matrix[subject_index][subject_index] += 1
            else:  # disagreement
                check_subject(map2[key])
                disagreement_subject_index = subject_index_map[map2[key]]
                matrix[subject_index][disagreement_subject_index] += 1

    return matrix


def cohen_kappa(data):

    # TODO: verify matrix, needs to be square, # needs to be > 1 and the dimension needs to be 2

    total_of_instances = sum(sum(data, []))

    if total_of_instances == 0:
        return {'k': 1, 'p_a': 1, 'p_e': 0}

    total_of_agreement = 0
    matrix_size = len(data)

    # p_e = the probability of random agreement, baseline agreement
    p_e = 0

    for i in range(0, matrix_size):
        total_of_agreement += data[i][i] # agreements are in the main diagonal

        marginal_frequency_observer_x = 0
        marginal_frequency_observer_y = 0

        for j in range(0, matrix_size):
            marginal_frequency_observer_x += data[i][j]
            marginal_frequency_observer_y += data[j][i]

        # p_e += probability of random agreement between x and y on i category
        p_e += (marginal_frequency_observer_x/total_of_instances)*(marginal_frequency_observer_y/total_of_instances)

    # p_a = the relative observed agreement among raters
    p_a = total_of_agreement/total_of_instances

    if p_a == 1 and p_e == 1:
        k = 1
    else:
        k = (p_a-p_e)/(1-p_e)

    return {'k': k, 'p_a': p_a, 'p_e': p_e}


def fleiss_kappa(data):
    pass

if __name__ == '__main__':

    # cohen_kappa_test_data = [[0 for x in range(3)] for y in range(3)]
    cohen_kappa_test_data = [
        [10, 4, 1],
        [6, 16, 2],
        [0, 3, 8]
    ]

    print(cohen_kappa(cohen_kappa_test_data))
