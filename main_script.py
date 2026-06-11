import re
# def extract_fault_lines(file_path):
#     """
#     Reads a .txt file, extracts lines containing 'has-fault-', and removes parentheses.
    
#     Args:
#         file_path (str): Path to the input .txt file
    
#     Returns:
#         list: A list of extracted lines without parentheses
#     """
#     extracted_lines = []
    
#     with open(file_path, 'r') as file:
#         for line in file:
#             line = line.strip()  # Remove leading/trailing whitespace
#             if "has-fault-" in line:
#                 cleaned_line = line.replace("(", "").replace(")", "")  # Remove parentheses
#                 extracted_lines.append(cleaned_line)
    
#     return extracted_lines

# def save_formatted_faults(fault_lines, output_file):
#     """
#     Formats the extracted fault lines and saves them to a text file.

#     Args:
#         fault_lines (list): A list of extracted lines containing 'has-fault-'.
#         output_file (str): Path to the output text file.
#     """
#     formatted_lines = []

#     for line in fault_lines:
#         formatted_line = f"(when (not ({line})) (and ({line}) (exe-{line})))"
#         formatted_lines.append(formatted_line)

#     # Write formatted lines to the output file
#     with open(output_file, 'w', encoding='utf-8') as file:
#         for line in formatted_lines:
#             file.write(line + '\n')

# # Example usage:
# file_path = "predicates.txt"  # Replace with the actual file path
# fault_lines = extract_fault_lines(file_path)

# # Print or use the extracted lines
# print(f"# of predicates extracted: {len(fault_lines)}")

# output_file = "formatted_faults.txt"  # Replace with desired output file path
# save_formatted_faults(fault_lines, output_file)

# print(f"Formatted faults saved to {output_file}")

def replace_fault_effects_in_pddl(input_file, output_file, new_effects):
    """
    Reads a domain.pddl file, finds actions whose names start with 'causes-fault-', 
    and replaces only their effect block with the provided new effect content.
    Other actions remain unchanged.

    Args:
        input_file (str): Path to the input domain.pddl file.
        output_file (str): Path to save the modified domain.pddl file.
        new_effects (str): The new effect content (inner content only, without outer parentheses)
                           to replace in matching actions.
    
    Returns:
        None
    """
    # Read the input file
    with open(input_file, 'r') as f:
        content = f.read()

    # The regex pattern explanation:
    #  - Group 1: Matches from "(:action" up to the ":effect" keyword and the following whitespace,
    #             then the literal "(" that starts the effect block.
    #  - Group 2: Matches the current effect block content (non-greedily, allowing newlines)
    #  - Group 3: Matches the closing ")" of the effect block along with any trailing whitespace and the
    #             closing ")" of the action definition.
    #
    # We use [\S]+ for the action name (assuming no whitespace in the name).
    pattern = re.compile(
        r'(\(:action\s+causes-fault-[\S]+\s*:parameters\s*\(.*?\)\s*:precondition\s*\(.*?\)\s*:effect\s*)\((.*?)\)(\s*\))',
        re.DOTALL
    )

    def repl(match):
        header = match.group(1)  # Up to and including the opening parenthesis of the effect
        tail = match.group(3)    # Closing part (closing parenthesis of effect and of the action)
        # Insert new_effects (wrapped in a new pair of parentheses) in place of the old effect content.
        return f"{header}({new_effects}){tail}"

    # Apply substitution over the entire file content
    modified_content = pattern.sub(repl, content)

    # Write the modified content to the output file
    with open(output_file, 'w') as f:
        f.write(modified_content)


input_pddl_file = "RG_ext/est_grounded_domain_all_faults-flare.pddl"  # Replace with the actual file path
output_pddl_file = "RG_ext/modified_domain_all_faults-flare.pddl"  # Output file name

new_effect_structure = """
(and
    (when (not (has-fault-pilot-extinction-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-pilot-extinction-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-pilot-extinction-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-instrumental-failure-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-instrumental-failure-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-instrumental-failure-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-pilot-supply-pipe-isolated-due-to-compromised_internal-network)) (and (has-fault-pilot-supply-pipe-isolated-due-to-compromised_internal-network) (exe-has-fault-pilot-supply-pipe-isolated-due-to-compromised_internal-network)))
    (when (not (has-fault-ignition-pipe-clogged-due-to-compromised_internal-network)) (and (has-fault-ignition-pipe-clogged-due-to-compromised_internal-network) (exe-has-fault-ignition-pipe-clogged-due-to-compromised_internal-network)))
    (when (not (has-fault-switching-to-another-flare-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-switching-to-another-flare-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-switching-to-another-flare-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-relief-pcv-closed-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-relief-pcv-closed-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-relief-pcv-closed-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-pcv-faulty-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-pcv-faulty-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-pcv-faulty-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-instrumental-failure-due-to-compromised_internal-network)) (and (has-fault-instrumental-failure-due-to-compromised_internal-network) (exe-has-fault-instrumental-failure-due-to-compromised_internal-network)))
    (when (not (has-fault-nitrogen-valve-open-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-nitrogen-valve-open-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-nitrogen-valve-open-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-defect-on-ignition-system-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-defect-on-ignition-system-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-defect-on-ignition-system-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-pilot-low-supply-pressure-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-instrumental-failure-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-instrumental-failure-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-instrumental-failure-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-ignition-pipe-clogged-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-ignition-pipe-clogged-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-ignition-pipe-clogged-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-pilot-extinction-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-pilot-extinction-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-pilot-extinction-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-opertor-fault-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-opertor-fault-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-opertor-fault-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-pumping-phenomenon-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-pumping-phenomenon-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-pumping-phenomenon-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_internal-network)) (and (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_internal-network) (exe-has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_internal-network)))
    (when (not (has-fault-pilot-extinction-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-pilot-extinction-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-pilot-extinction-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-pilot-extinction-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-pilot-extinction-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-pilot-extinction-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-ignition-pipe-clogged-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-ignition-pipe-clogged-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-ignition-pipe-clogged-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-mechanical-failure-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-mechanical-failure-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-mechanical-failure-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-pcv-faulty-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-pcv-faulty-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-pcv-faulty-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-manual-isolation-valve-close-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-manual-isolation-valve-close-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-manual-isolation-valve-close-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-switching-to-another-flare-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-switching-to-another-flare-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-switching-to-another-flare-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-low-flow-gas-flaring-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-low-flow-gas-flaring-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-low-flow-gas-flaring-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-manual-isolation-valve-close-due-to-compromised_firewall-vpn)) (and (has-fault-manual-isolation-valve-close-due-to-compromised_firewall-vpn) (exe-has-fault-manual-isolation-valve-close-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-fg-interrupted-at-source-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-fg-interrupted-at-source-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-fg-interrupted-at-source-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-isolation-of-fg-line-for-works-due-to-compromised_internal-network)) (and (has-fault-isolation-of-fg-line-for-works-due-to-compromised_internal-network) (exe-has-fault-isolation-of-fg-line-for-works-due-to-compromised_internal-network)))
    (when (not (has-fault-condensate-presence-in-fg-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-condensate-presence-in-fg-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-condensate-presence-in-fg-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-defect-on-ignition-system-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-defect-on-ignition-system-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-defect-on-ignition-system-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-pcv-faulty-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-pcv-faulty-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-pcv-faulty-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-isolation-of-fg-line-for-works-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-isolation-of-fg-line-for-works-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-isolation-of-fg-line-for-works-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-pilot-supply-pipe-isolated-due-to-compromised_firewall-vpn)) (and (has-fault-pilot-supply-pipe-isolated-due-to-compromised_firewall-vpn) (exe-has-fault-pilot-supply-pipe-isolated-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-manual-isolation-valve-close-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-manual-isolation-valve-close-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-manual-isolation-valve-close-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-pumping-phenomenon-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-pumping-phenomenon-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-pumping-phenomenon-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-pilot-low-supply-pressure-due-to-compromised_firewall-vpn)) (and (has-fault-pilot-low-supply-pressure-due-to-compromised_firewall-vpn) (exe-has-fault-pilot-low-supply-pressure-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-mechanical-failure-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-mechanical-failure-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-mechanical-failure-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-fg-interrupted-at-source-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-fg-interrupted-at-source-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-fg-interrupted-at-source-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-switching-to-another-flare-due-to-compromised_internal-network)) (and (has-fault-switching-to-another-flare-due-to-compromised_internal-network) (exe-has-fault-switching-to-another-flare-due-to-compromised_internal-network)))
    (when (not (has-fault-manual-isolation-valve-close-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-manual-isolation-valve-close-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-manual-isolation-valve-close-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-opertor-fault-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-opertor-fault-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-opertor-fault-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-flame-detachment-due-to-compromised_internal-network)) (and (has-fault-flame-detachment-due-to-compromised_internal-network) (exe-has-fault-flame-detachment-due-to-compromised_internal-network)))
    (when (not (has-fault-pcv-faulty-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-pcv-faulty-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-pcv-faulty-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-nitrogen-valve-open-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-nitrogen-valve-open-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-nitrogen-valve-open-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-relief-pcv-closed-to-compromised_internal-network)) (and (has-fault-relief-pcv-closed-to-compromised_internal-network) (exe-has-fault-relief-pcv-closed-to-compromised_internal-network)))
    (when (not (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-pilot-low-supply-pressure-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-relief-pcv-closed-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-relief-pcv-closed-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-relief-pcv-closed-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-pilot-low-supply-pressure-due-to-compromised_internal-network)) (and (has-fault-pilot-low-supply-pressure-due-to-compromised_internal-network) (exe-has-fault-pilot-low-supply-pressure-due-to-compromised_internal-network)))
    (when (not (has-fault-mechanical-failure-due-to-compromised_internal-network)) (and (has-fault-mechanical-failure-due-to-compromised_internal-network) (exe-has-fault-mechanical-failure-due-to-compromised_internal-network)))
    (when (not (has-fault-mechanical-failure-due-to-compromised_firewall-vpn)) (and (has-fault-mechanical-failure-due-to-compromised_firewall-vpn) (exe-has-fault-mechanical-failure-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-nitrogen-valve-open-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-nitrogen-valve-open-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-nitrogen-valve-open-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-failure-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-failure-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-failure-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-failure-on-ignition-system-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-failure-on-ignition-system-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-failure-on-ignition-system-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-pumping-phenomenon-due-to-compromised_internal-network)) (and (has-fault-pumping-phenomenon-due-to-compromised_internal-network) (exe-has-fault-pumping-phenomenon-due-to-compromised_internal-network)))
    (when (not (has-fault-switching-to-another-flare-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-switching-to-another-flare-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-switching-to-another-flare-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-pcv-faulty-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-pcv-faulty-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-pcv-faulty-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-pilot-extinction-due-to-compromised_firewall-vpn)) (and (has-fault-pilot-extinction-due-to-compromised_firewall-vpn) (exe-has-fault-pilot-extinction-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-opertor-fault-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-opertor-fault-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-opertor-fault-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-mechanical-failure-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-mechanical-failure-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-mechanical-failure-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-relief-pcv-closed-to-compromised_microsoft-windows-12-server)) (and (has-fault-relief-pcv-closed-to-compromised_microsoft-windows-12-server) (exe-has-fault-relief-pcv-closed-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-fg-interrupted-at-source-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-fg-interrupted-at-source-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-fg-interrupted-at-source-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-pilot-low-supply-pressure-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-pilot-low-supply-pressure-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-pilot-low-supply-pressure-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-switching-to-another-flare-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-switching-to-another-flare-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-switching-to-another-flare-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-condensate-presence-in-fg-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-condensate-presence-in-fg-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-condensate-presence-in-fg-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-no-flow-of-fuel-gas-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-no-flow-of-fuel-gas-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-no-flow-of-fuel-gas-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-defect-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-defect-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-defect-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-low-flow-gas-flaring-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-low-flow-gas-flaring-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-low-flow-gas-flaring-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-mechanical-failure-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-mechanical-failure-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-mechanical-failure-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-ignition-pipe-clogged-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-ignition-pipe-clogged-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-ignition-pipe-clogged-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-opertor-fault-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-opertor-fault-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-opertor-fault-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-relief-pcv-closed-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-relief-pcv-closed-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-relief-pcv-closed-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-ignition-pipe-clogged-due-to-compromised_firewall-vpn)) (and (has-fault-ignition-pipe-clogged-due-to-compromised_firewall-vpn) (exe-has-fault-ignition-pipe-clogged-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-low-flow-gas-flaring-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-low-flow-gas-flaring-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-low-flow-gas-flaring-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-condensate-presence-in-fg-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-condensate-presence-in-fg-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-condensate-presence-in-fg-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-opertor-fault-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-opertor-fault-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-opertor-fault-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-flame-detachment-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-flame-detachment-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-flame-detachment-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-switching-to-another-flare-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-switching-to-another-flare-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-switching-to-another-flare-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-valve-blocked-close-due-to-compromised_firewall-vpn)) (and (has-fault-valve-blocked-close-due-to-compromised_firewall-vpn) (exe-has-fault-valve-blocked-close-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-relief-pcv-closed-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-relief-pcv-closed-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-relief-pcv-closed-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-opertor-fault-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-opertor-fault-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-opertor-fault-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-mechanical-failure-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-mechanical-failure-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-mechanical-failure-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-defect-on-ignition-system-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-defect-on-ignition-system-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-defect-on-ignition-system-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-switching-to-another-flare-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-switching-to-another-flare-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-switching-to-another-flare-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-failure-on-ignition-system-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-failure-on-ignition-system-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-failure-on-ignition-system-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-instrumental-failure-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-instrumental-failure-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-instrumental-failure-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-pilot-extinction-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-pilot-extinction-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-pilot-extinction-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-failure-on-ignition-system-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-failure-on-ignition-system-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-failure-on-ignition-system-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-fg-interrupted-at-source-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-fg-interrupted-at-source-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-fg-interrupted-at-source-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-pilot-low-supply-pressure-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-pumping-phenomenon-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-pumping-phenomenon-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-pumping-phenomenon-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-pumping-phenomenon-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-pumping-phenomenon-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-pumping-phenomenon-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-flame-detachment-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-flame-detachment-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-flame-detachment-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-valve-blocked-close-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-valve-blocked-close-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-valve-blocked-close-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-failure-on-ignition-system-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-failure-on-ignition-system-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-failure-on-ignition-system-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-instrumental-failure-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-instrumental-failure-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-instrumental-failure-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-valve-blocked-close-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-valve-blocked-close-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-valve-blocked-close-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-low-flow-gas-flaring-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-low-flow-gas-flaring-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-low-flow-gas-flaring-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-mechanical-failure-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-mechanical-failure-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-mechanical-failure-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-valve-blocked-close-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-valve-blocked-close-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-valve-blocked-close-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-switching-to-another-flare-due-to-compromised_firewall-vpn)) (and (has-fault-switching-to-another-flare-due-to-compromised_firewall-vpn) (exe-has-fault-switching-to-another-flare-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-nitrogen-valve-open-due-to-compromised_internal-network)) (and (has-fault-nitrogen-valve-open-due-to-compromised_internal-network) (exe-has-fault-nitrogen-valve-open-due-to-compromised_internal-network)))
    (when (not (has-fault-manual-isolation-valve-close-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-manual-isolation-valve-close-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-manual-isolation-valve-close-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-defect-on-ignition-system-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-defect-on-ignition-system-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-defect-on-ignition-system-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-flame-detachment-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-flame-detachment-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-flame-detachment-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-pumping-phenomenon-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-pumping-phenomenon-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-pumping-phenomenon-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-no-flow-of-fuel-gas-due-to-compromised_internal-network)) (and (has-fault-no-flow-of-fuel-gas-due-to-compromised_internal-network) (exe-has-fault-no-flow-of-fuel-gas-due-to-compromised_internal-network)))
    (when (not (has-fault-fg-interrupted-at-source-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-fg-interrupted-at-source-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-fg-interrupted-at-source-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-opertor-fault-due-to-compromised_firewall-vpn)) (and (has-fault-opertor-fault-due-to-compromised_firewall-vpn) (exe-has-fault-opertor-fault-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-manual-isolation-valve-close-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-manual-isolation-valve-close-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-manual-isolation-valve-close-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-failure-on-ignition-system-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-failure-on-ignition-system-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-failure-on-ignition-system-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-flame-detachment-due-to-compromised_firewall-vpn)) (and (has-fault-flame-detachment-due-to-compromised_firewall-vpn) (exe-has-fault-flame-detachment-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-fg-interrupted-at-source-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-fg-interrupted-at-source-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-fg-interrupted-at-source-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-pilot-extinction-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-pilot-extinction-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-pilot-extinction-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-valve-blocked-close-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-valve-blocked-close-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-valve-blocked-close-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-nitrogen-valve-open-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-nitrogen-valve-open-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-nitrogen-valve-open-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-defect-on-ignition-system-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-defect-on-ignition-system-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-defect-on-ignition-system-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-instrumental-failure-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-instrumental-failure-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-instrumental-failure-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-failure-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-failure-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-failure-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-ignition-pipe-clogged-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-ignition-pipe-clogged-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-ignition-pipe-clogged-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-pilot-low-supply-pressure-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-condensate-presence-in-fg-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-condensate-presence-in-fg-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-condensate-presence-in-fg-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-valve-blocked-close-due-to-compromised_internal-network)) (and (has-fault-valve-blocked-close-due-to-compromised_internal-network) (exe-has-fault-valve-blocked-close-due-to-compromised_internal-network)))
    (when (not (has-fault-ignition-pipe-clogged-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-ignition-pipe-clogged-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-ignition-pipe-clogged-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-condensate-presence-in-fg-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-condensate-presence-in-fg-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-condensate-presence-in-fg-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-fg-interrupted-at-source-due-to-compromised_internal-network)) (and (has-fault-fg-interrupted-at-source-due-to-compromised_internal-network) (exe-has-fault-fg-interrupted-at-source-due-to-compromised_internal-network)))
    (when (not (has-fault-opertor-fault-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-opertor-fault-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-opertor-fault-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-low-flow-gas-flaring-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-low-flow-gas-flaring-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-low-flow-gas-flaring-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-relief-pcv-closed-to-compromised_firewall-vpn)) (and (has-fault-relief-pcv-closed-to-compromised_firewall-vpn) (exe-has-fault-relief-pcv-closed-to-compromised_firewall-vpn)))
    (when (not (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-low-flow-gas-flaring-due-to-compromised_firewall-vpn)) (and (has-fault-low-flow-gas-flaring-due-to-compromised_firewall-vpn) (exe-has-fault-low-flow-gas-flaring-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-nitrogen-valve-open-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-nitrogen-valve-open-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-nitrogen-valve-open-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-flame-detachment-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-flame-detachment-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-flame-detachment-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-relief-pcv-closed-to-compromised_plc-siemens-s7-1200)) (and (has-fault-relief-pcv-closed-to-compromised_plc-siemens-s7-1200) (exe-has-fault-relief-pcv-closed-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-relief-pcv-closed-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-relief-pcv-closed-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-relief-pcv-closed-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-nitrogen-valve-open-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-nitrogen-valve-open-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-nitrogen-valve-open-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-condensate-presence-in-fg-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-condensate-presence-in-fg-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-condensate-presence-in-fg-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-pilot-extinction-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-pilot-extinction-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-pilot-extinction-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-manual-isolation-valve-close-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-manual-isolation-valve-close-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-manual-isolation-valve-close-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-defect-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-defect-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-defect-on-ignition-system-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-mechanical-failure-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-mechanical-failure-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-mechanical-failure-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-manual-isolation-valve-close-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-manual-isolation-valve-close-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-manual-isolation-valve-close-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-condensate-presence-in-fg-due-to-compromised_internal-network)) (and (has-fault-condensate-presence-in-fg-due-to-compromised_internal-network) (exe-has-fault-condensate-presence-in-fg-due-to-compromised_internal-network)))
    (when (not (has-fault-failure-on-ignition-system-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-failure-on-ignition-system-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-failure-on-ignition-system-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-fg-interrupted-at-source-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-fg-interrupted-at-source-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-fg-interrupted-at-source-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-switching-to-another-flare-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-switching-to-another-flare-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-switching-to-another-flare-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-pilot-low-supply-pressure-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-pilot-extinction-due-to-compromised_internal-network)) (and (has-fault-pilot-extinction-due-to-compromised_internal-network) (exe-has-fault-pilot-extinction-due-to-compromised_internal-network)))
    (when (not (has-fault-switching-to-another-flare-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-switching-to-another-flare-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-switching-to-another-flare-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-condensate-presence-in-fg-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-condensate-presence-in-fg-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-condensate-presence-in-fg-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-fg-interrupted-at-source-due-to-compromised_firewall-vpn)) (and (has-fault-fg-interrupted-at-source-due-to-compromised_firewall-vpn) (exe-has-fault-fg-interrupted-at-source-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-pumping-phenomenon-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-pumping-phenomenon-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-pumping-phenomenon-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-ignition-pipe-clogged-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-ignition-pipe-clogged-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-ignition-pipe-clogged-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-pumping-phenomenon-due-to-compromised_firewall-vpn)) (and (has-fault-pumping-phenomenon-due-to-compromised_firewall-vpn) (exe-has-fault-pumping-phenomenon-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-pilot-low-supply-pressure-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-isolation-of-fg-line-for-works-due-to-compromised_firewall-vpn)) (and (has-fault-isolation-of-fg-line-for-works-due-to-compromised_firewall-vpn) (exe-has-fault-isolation-of-fg-line-for-works-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-condensate-presence-in-fg-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-condensate-presence-in-fg-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-condensate-presence-in-fg-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-defect-on-ignition-system-due-to-compromised_internal-network)) (and (has-fault-defect-on-ignition-system-due-to-compromised_internal-network) (exe-has-fault-defect-on-ignition-system-due-to-compromised_internal-network)))
    (when (not (has-fault-nitrogen-valve-open-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-nitrogen-valve-open-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-nitrogen-valve-open-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-ignition-pipe-clogged-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-ignition-pipe-clogged-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-ignition-pipe-clogged-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-pumping-phenomenon-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-pumping-phenomenon-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-pumping-phenomenon-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-valve-blocked-close-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-valve-blocked-close-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-valve-blocked-close-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-failure-on-ignition-system-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-failure-on-ignition-system-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-failure-on-ignition-system-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_firewall-vpn)) (and (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_firewall-vpn) (exe-has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-low-flow-gas-flaring-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-low-flow-gas-flaring-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-low-flow-gas-flaring-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-opertor-fault-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-opertor-fault-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-opertor-fault-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-manual-isolation-valve-close-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-manual-isolation-valve-close-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-manual-isolation-valve-close-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-fg-interrupted-at-source-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-fg-interrupted-at-source-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-fg-interrupted-at-source-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-instrumental-failure-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-instrumental-failure-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-instrumental-failure-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-opertor-fault-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-opertor-fault-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-opertor-fault-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-pcv-faulty-due-to-compromised_internal-network)) (and (has-fault-pcv-faulty-due-to-compromised_internal-network) (exe-has-fault-pcv-faulty-due-to-compromised_internal-network)))
    (when (not (has-fault-mechanical-failure-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-mechanical-failure-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-mechanical-failure-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-manual-isolation-valve-close-due-to-compromised_internal-network)) (and (has-fault-manual-isolation-valve-close-due-to-compromised_internal-network) (exe-has-fault-manual-isolation-valve-close-due-to-compromised_internal-network)))
    (when (not (has-fault-valve-blocked-close-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-valve-blocked-close-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-valve-blocked-close-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-pcv-faulty-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-pcv-faulty-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-pcv-faulty-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-mechanical-failure-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-mechanical-failure-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-mechanical-failure-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-flame-detachment-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-flame-detachment-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-flame-detachment-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-pilot-low-supply-pressure-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-switching-to-another-flare-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-switching-to-another-flare-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-switching-to-another-flare-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-nitrogen-valve-open-due-to-compromised_firewall-vpn)) (and (has-fault-nitrogen-valve-open-due-to-compromised_firewall-vpn) (exe-has-fault-nitrogen-valve-open-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-instrumental-failure-due-to-compromised_firewall-vpn)) (and (has-fault-instrumental-failure-due-to-compromised_firewall-vpn) (exe-has-fault-instrumental-failure-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-pilot-supply-pipe-isolated-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-fg-interrupted-at-source-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-fg-interrupted-at-source-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-fg-interrupted-at-source-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-relief-pcv-closed-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-relief-pcv-closed-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-relief-pcv-closed-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-valve-blocked-close-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-valve-blocked-close-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-valve-blocked-close-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-low-flow-gas-flaring-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-low-flow-gas-flaring-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-low-flow-gas-flaring-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-relief-pcv-closed-to-compromised_plc-yokogawa-stardom)) (and (has-fault-relief-pcv-closed-to-compromised_plc-yokogawa-stardom) (exe-has-fault-relief-pcv-closed-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-valve-blocked-close-due-to-compromised_plc-siemens-s7-1200)) (and (has-fault-valve-blocked-close-due-to-compromised_plc-siemens-s7-1200) (exe-has-fault-valve-blocked-close-due-to-compromised_plc-siemens-s7-1200)))
    (when (not (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-ignition-pipe-clogged-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-ignition-pipe-clogged-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-ignition-pipe-clogged-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-instrumental-failure-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-instrumental-failure-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-instrumental-failure-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-condensate-presence-in-fg-due-to-compromised_firewall-vpn)) (and (has-fault-condensate-presence-in-fg-due-to-compromised_firewall-vpn) (exe-has-fault-condensate-presence-in-fg-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-pcv-faulty-due-to-compromised_firewall-vpn)) (and (has-fault-pcv-faulty-due-to-compromised_firewall-vpn) (exe-has-fault-pcv-faulty-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-flame-detachment-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-flame-detachment-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-flame-detachment-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-nitrogen-valve-open-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-nitrogen-valve-open-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-nitrogen-valve-open-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-failure-on-ignition-system-due-to-compromised_internal-network)) (and (has-fault-failure-on-ignition-system-due-to-compromised_internal-network) (exe-has-fault-failure-on-ignition-system-due-to-compromised_internal-network)))
    (when (not (has-fault-low-flow-gas-flaring-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-low-flow-gas-flaring-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-low-flow-gas-flaring-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-instrumental-failure-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-instrumental-failure-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-instrumental-failure-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-no-flow-of-fuel-gas-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-low-flow-gas-flaring-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-low-flow-gas-flaring-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-low-flow-gas-flaring-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-defect-on-ignition-system-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-defect-on-ignition-system-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-defect-on-ignition-system-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-no-flow-of-fuel-gas-due-to-compromised_firewall-vpn)) (and (has-fault-no-flow-of-fuel-gas-due-to-compromised_firewall-vpn) (exe-has-fault-no-flow-of-fuel-gas-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-manual-isolation-valve-close-due-to-compromised_plc-schneider-electric-modicon-m221)) (and (has-fault-manual-isolation-valve-close-due-to-compromised_plc-schneider-electric-modicon-m221) (exe-has-fault-manual-isolation-valve-close-due-to-compromised_plc-schneider-electric-modicon-m221)))
    (when (not (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-pilot-low-supply-pressure-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-pilot-low-supply-pressure-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-pcv-faulty-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-pcv-faulty-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-pcv-faulty-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-pcv-faulty-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-pcv-faulty-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-pcv-faulty-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-windspeed-greater-than-120-km-per-hr-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-instrumental-failure-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-instrumental-failure-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-instrumental-failure-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-condensate-presence-in-fg-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-condensate-presence-in-fg-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-condensate-presence-in-fg-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-pilot-extinction-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-pilot-extinction-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-pilot-extinction-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-low-flow-gas-flaring-due-to-compromised_internal-network)) (and (has-fault-low-flow-gas-flaring-due-to-compromised_internal-network) (exe-has-fault-low-flow-gas-flaring-due-to-compromised_internal-network)))
    (when (not (has-fault-pumping-phenomenon-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-pumping-phenomenon-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-pumping-phenomenon-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-pipe-not-drained)) (and (has-fault-pipe-not-drained) (exe-has-fault-pipe-not-drained)))
    (when (not (has-fault-ignition-pipe-clogged-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-ignition-pipe-clogged-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-ignition-pipe-clogged-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-pilot-extinction-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-pilot-extinction-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-pilot-extinction-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-pumping-phenomenon-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-pumping-phenomenon-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-pumping-phenomenon-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-isolation-of-fg-line-for-works-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-opertor-fault-due-to-compromised_internal-network)) (and (has-fault-opertor-fault-due-to-compromised_internal-network) (exe-has-fault-opertor-fault-due-to-compromised_internal-network)))
    (when (not (has-fault-pilot-supply-pipe-isolated-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-pilot-supply-pipe-isolated-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-pilot-supply-pipe-isolated-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-defect-on-ignition-system-due-to-compromised_plc-mitsubishi-melsec-q-series)) (and (has-fault-defect-on-ignition-system-due-to-compromised_plc-mitsubishi-melsec-q-series) (exe-has-fault-defect-on-ignition-system-due-to-compromised_plc-mitsubishi-melsec-q-series)))
    (when (not (has-fault-failure-on-ignition-system-due-to-compromised_firewall-vpn)) (and (has-fault-failure-on-ignition-system-due-to-compromised_firewall-vpn) (exe-has-fault-failure-on-ignition-system-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-flame-detachment-due-to-compromised_plc-allen-brdley-controllogix)) (and (has-fault-flame-detachment-due-to-compromised_plc-allen-brdley-controllogix) (exe-has-fault-flame-detachment-due-to-compromised_plc-allen-brdley-controllogix)))
    (when (not (has-fault-pcv-faulty-due-to-compromised_plc-siemens-s7-300-or-400)) (and (has-fault-pcv-faulty-due-to-compromised_plc-siemens-s7-300-or-400) (exe-has-fault-pcv-faulty-due-to-compromised_plc-siemens-s7-300-or-400)))
    (when (not (has-fault-flame-detachment-due-to-compromised_plc-yokogawa-stardom)) (and (has-fault-flame-detachment-due-to-compromised_plc-yokogawa-stardom) (exe-has-fault-flame-detachment-due-to-compromised_plc-yokogawa-stardom)))
    (when (not (has-fault-flame-detachment-due-to-compromised_microsoft-windows-12-server)) (and (has-fault-flame-detachment-due-to-compromised_microsoft-windows-12-server) (exe-has-fault-flame-detachment-due-to-compromised_microsoft-windows-12-server)))
    (when (not (has-fault-valve-blocked-close-due-to-compromised_plc-schneider-electric-modicon-m580)) (and (has-fault-valve-blocked-close-due-to-compromised_plc-schneider-electric-modicon-m580) (exe-has-fault-valve-blocked-close-due-to-compromised_plc-schneider-electric-modicon-m580)))
    (when (not (has-fault-defect-on-ignition-system-due-to-compromised_firewall-vpn)) (and (has-fault-defect-on-ignition-system-due-to-compromised_firewall-vpn) (exe-has-fault-defect-on-ignition-system-due-to-compromised_firewall-vpn)))
    (when (not (has-fault-nitrogen-valve-open-due-to-compromised_plc-allen-bradley-micrologix-1100)) (and (has-fault-nitrogen-valve-open-due-to-compromised_plc-allen-bradley-micrologix-1100) (exe-has-fault-nitrogen-valve-open-due-to-compromised_plc-allen-bradley-micrologix-1100)))
    (when (not (has-fault-flare-flameout)) (and (has-fault-flare-flameout) (exe-has-fault-flare-flameout)))
    (increase (total-cost) 1)
)
"""  # Replace this with your desired new effect structure
replace_fault_effects_in_pddl(input_pddl_file, output_pddl_file, new_effect_structure)





