library IEEE;
use IEEE.std_logic_1164.all;
use work.CPU_library.all;

entity CPU_tb is
end CPU_tb;

architecture testbench of CPU_tb is
	
	constant DATA_WIDTH 	: integer := 16;
	constant ADDRESS_WIDTH: integer := 16;
	constant clk_period 	: time := 100 ps;
	
	signal finishFlag 	: std_logic := '0';
	
	-- CPU Signals
	signal instruction	: std_logic_vector((DATA_WIDTH-1) downto 0);
	signal CLK				: std_logic;
	signal Reset 			: std_logic;
	signal Mem_write		: std_logic;
	signal Mem_read		: std_logic;
	signal i_address		: std_logic_vector((ADDRESS_WIDTH-1) downto 0);
	signal i_data			: std_logic_vector((DATA_WIDTH-1) downto 0);
	signal Cu_state		: std_logic_vector(3 downto 0);
	signal flags			: std_logic_vector(4 downto 0);		

	
begin
	
	-- Unit Under Test Portmap
	UUT: entity work.CPU(structural) generic map(DATA_WIDTH) port map(instruction, CLK, Reset, Mem_write, Mem_read, i_address, i_data, cu_state, flags);
	
	-- Connect Memory to CPU
	RAM: entity work.Memory(Behavioral) generic map(DATA_WIDTH, ADDRESS_WIDTH) port map(i_data, Mem_write, Mem_read, i_address, CLK, instruction);
	
	-- Clock Generation Process
	Clock: process
	begin
	
		CLK <= '1';
		wait for clk_period/2;
		CLK <= '0';
		wait for clk_period/2;
		
		if finishFlag = '1' then
			wait;
		end if;
		
	end process;
	
	-- Simulation Process
	Stimulus: process
	begin
	
		Reset <= '1';
		wait for clk_period + clk_period/2;
		Reset <= '0';
		wait for clk_period*50;
	
	
		finishFlag <= '1';
		wait;
	
	end process;
	

end testbench;