import signal
import multiprocessing
import logging

from spectral_network import SpectralNetwork


def child_sigint_handler(signum, frame):
    # print("SIGINT catched by a child of loom.parallel.")
    raise KeyboardInterrupt("SIGINT catched by a child of loom.parallel.")


def child_sigterm_handler(signum, frame):
    print("SIGTERM catched by a child of loom.parallel.")
    raise SystemExit("SIGTERM catched by a child of loom.parallel.")


def init_process():
    """
    Initializer of each child process that generates a spectral network.
    Take care of a keyboard interrupt and a SIGTERM.
    """
    signal.signal(signal.SIGINT, child_sigint_handler)
    # signal.signal(signal.SIGTERM, child_sigterm_handler)


def a_child_process(
    sw,
    phase,
    config,
    shared_n_started_spectral_networks,
    shared_n_finished_spectral_networks,
    logger_name,
):
    logger = logging.getLogger(logger_name)
    theta_i, theta_f, theta_n = config['phase']

    shared_n_started_spectral_networks.value += 1
    job_id = shared_n_started_spectral_networks.value
    logger.info('Start generating spectral network #{}/{}: theta = {}.'
                .format(job_id, theta_n, phase))
   
    try:
        spectral_network = SpectralNetwork(
            phase=phase, 
            logger_name=logger_name,
        ) 

        spectral_network.grow(config, sw)
#    except (KeyboardInterrupt, SystemExit) as e:
#        logger.warning('A child process calculating phase = {} '
#                       'caught {}'.format(phase, type(e)))
#        return None
    except Exception as e:
        logger.warning('A child process calculating phase = {} '
                       'caught an exception: {}'.format(phase, e))
        spectral_network.errors.append = ('Unknown', e.args)
#        return None 

    shared_n_finished_spectral_networks.value += 1
    logger.info('Finished generating spectral network #{}/{}.'
                .format(shared_n_finished_spectral_networks.value, theta_n))

    return spectral_network


def parallel_get_spectral_network(
    sw, 
    config,
    n_processes,
    logger_name='loom',
):
    logger = logging.getLogger(logger_name)
    spectral_network_list = []

    theta_i, theta_f, theta_n = config['phase']
    phases = [(float(theta_i) + i * float(theta_f - theta_i) / (theta_n - 1))
              for i in range(theta_n)]

    manager = multiprocessing.Manager()
    shared_n_started_spectral_networks = manager.Value('i', 0)
    shared_n_finished_spectral_networks = manager.Value('i', 0)

    n_cpu = multiprocessing.cpu_count()
    if (n_processes == 0):
        # Use all the CPUs.
        n_processes = n_cpu
    elif (n_processes < 0):
        # Leave |n_processes| CPUs.
        if(n_cpu > -n_processes):
            n_processes = n_cpu - (-n_processes)
        else:
            logger.warning('The number of CPUs is smaller than {}.'
                           .format(-config['n_processes']))
            logger.warning('Set n_processes to 1.')
            n_processes = 1
    elif (n_cpu < n_processes):
            logger.warning('The number of CPUs is smaller than {}.'
                           .format(config['n_processes']))
            logger.warning('Set n_processes to {}.'.format(n_cpu))
            n_processes = n_cpu

    # Use n_processes CPUs.
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool(n_processes, init_process)
    logger.info('Number of processes in the pool: {}'.format(n_processes))

    try:
        results = [
            pool.apply_async(
                a_child_process,
                args=(
                    sw,
                    phase,
                    config,
                    shared_n_started_spectral_networks,
                    shared_n_finished_spectral_networks,
                    logger_name,
                )
            ) for phase in phases
        ]
        pool.close()

        for result in results:
            spectral_network_list.append(result.get())

    except (KeyboardInterrupt, SystemExit) as e:
        logger.warning('loom.parallel caught {}: {}; terminates processes...'
                       .format(type(e), e.args,))
        pool.terminate()
        pool.join()
        raise

    return spectral_network_list
