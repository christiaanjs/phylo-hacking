import pathlib
import random
import jinja2
from Bio import Phylo
import io
import xml

template_dir = 'templates'
class TemplateBuilder:
    def __init__(self, out_dir):
        self.out_path = pathlib.Path(out_dir)
        self.template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
        self.tree_sim_template_file = 'sim-tree.j2.xml'
        self.tree_sim_out_file = 'sim-tree.xml'
        self.tree_sim_out_path = self.out_path / self.tree_sim_out_file
        self.tree_sim_result_file = 'sim-tree.trees'
        self.tree_sim_result_path = self.out_path / self.tree_sim_result_file
        
        self.seq_sim_template_file = 'sim-seq.j2.xml'
        self.seq_sim_out_file = 'sim-seq.xml'
        self.seq_sim_out_path = self.out_path / self.seq_sim_out_file
        self.seq_sim_result_file = 'sequences.xml'
        self.seq_sim_result_path = self.out_path / self.seq_sim_result_file

        self.seq_sim_result_file = 'sequences.xml'
        self.seq_sim_result_path = self.out_path / self.seq_sim_result_file

        self.beast_analysis_template_file = 'beast-analysis.j2.xml'
        self.beast_analysis_out_file = 'beast-analysis.xml'
        self.beast_analysis_out_path = self.out_path / self.beast_analysis_out_file
        self.beast_analysis_tree_file = 'beast-log.trees'
        self.beast_analysis_tree_path = self.out_path / self.beast_analysis_tree_file
        self.beast_analysis_trace_file = 'beast-log.log'
        self.beast_analysis_trace_path = self.out_path / self.beast_analysis_trace_file

        self.pymc_analysis_result_file = 'pymc_tracker.pickle'
        self.pymc_analysis_result_path = self.out_path / self.pymc_analysis_result_file
        
        self.run_summary_file = 'run_summary.yaml'
        self.run_summary_path = self.out_path / self.run_summary_file

        self.run_results_file = 'results.csv'
        self.run_results_path = self.out_path / self.run_results_file

        self.nuts_trace_file = 'nuts.pickle'
        self.nuts_trace_path = self.out_path / self.nuts_trace_file

    def build_tree_sim(self, config):
        min_pop_size, max_pop_size, sampling_window, n_taxa = config['min_pop_size'], config['max_pop_size'], config['sampling_window'], config['n_taxa'] 
        pop_size = int(random.random() * (max_pop_size - min_pop_size) + min_pop_size)
        sampling_times = [random.random() * sampling_window for i in range(n_taxa)]
        taxon_names = ["T{}".format(i) for i in range(n_taxa)]
        date_trait_string = ','.join(['{0}={1}'.format(taxon_name, sampling_time) for taxon_name, sampling_time in zip(taxon_names, sampling_times)])

        tree_sim_template = self.template_env.get_template(self.tree_sim_template_file)
        tree_sim_string = tree_sim_template.render(pop_size=pop_size, date_trait_string=date_trait_string, taxon_names=taxon_names, out_file=self.tree_sim_result_path)  

        with open(self.tree_sim_out_path, 'w') as f:
            f.write(tree_sim_string)
        
        return pop_size, taxon_names, date_trait_string

    def extract_newick_string(self):
        with io.StringIO() as s:
            Phylo.convert(self.tree_sim_result_path, 'nexus', s, 'newick')
            newick_string = s.getvalue().strip()
        return newick_string

    def build_seq_sim(self, config, taxon_names, newick_string):
        seq_sim_template = self.template_env.get_template(self.seq_sim_template_file)
        seq_sim_string = seq_sim_template.render(
            taxon_names=taxon_names,
            newick_string=newick_string,
            out_file=self.seq_sim_result_path, **config)

        with open(self.seq_sim_out_path, 'w') as f:
            f.write(seq_sim_string)

    def extract_sequence_dict(self):
        seq_xml_root = xml.etree.ElementTree.parse(self.seq_sim_result_path)
        sequence_dict = { tag.attrib['taxon']: tag.attrib['value'] for tag in seq_xml_root.findall('./sequence') }
        return sequence_dict

    def build_beast_analysis(self, config, newick_string, date_trait_string, sequence_dict):
        beast_analysis_template = self.template_env.get_template(self.beast_analysis_template_file)
        beast_analysis_string = beast_analysis_template.render(
            newick_string=newick_string,
            sequence_dict=sequence_dict,
            date_trait_string=date_trait_string,
            trace_out_path=self.beast_analysis_trace_path,
            tree_out_path=self.beast_analysis_tree_path,
            **config
        )

        with open(self.beast_analysis_out_path, 'w') as f:
            f.write(beast_analysis_string)

    
