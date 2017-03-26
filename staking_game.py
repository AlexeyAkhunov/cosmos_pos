""" Attempt to simulate a staking game for Cosmos PoS when number of validators is limited to a certain number,
    say 100. Essentially, all the accounts holding atoms are sorted in the descending order of their atom
    holdings, then top 100 are selected, and those become validators.
    If we assume for a moment that there is no unbonding delay (which is in reality going to be 1 month),
    a large atom holder might find it beneficial to splits their holdings into multiple accounts, to
    occupy as many places in the top 100 list as possible, in order to get a maximum influence
"""

EPS = 0.1


class Scenario(object):

    def __init__(self, number_of_validators):
        self.number_of_validators = number_of_validators
        # holdings is a list of holdings for each atom holder. Atom holders are identified
        # by integers 0, 1, 2, ...
        self.holdings = []
        # distribution is a dictionary that maps holder identifier (integer) to a list of amounts
        # that shows how the holding is split among the accounts
        self.distribution = {}

    def set_holdings(self, holdings):
        """ Sets distribution of atoms
                distribution - list of numbers, each representing the holding of corresponding atom holder
        """
        # First, produce trivial distribution, one account per holder
        self.holdings = holdings
        for holder, amount in enumerate(holdings):
            self.distribution[holder] = [amount]

    def optimize_holder(self, holder):
        """ Optimizes the game for specified holder
            Returns true if there were actual changes made to the distribution
            (for testing the convergence)
        """
        a_old = self.distribution[holder]
        # Step 1 - remove holder's holdings from the distribution
        del self.distribution[holder]
        # Step 2 - produce the list of top holders
        all_amounts = [amount for amounts in self.distribution.values() for amount in amounts]
        top_amounts = sorted(all_amounts)[-self.number_of_validators:]
        # Step 3 - find optimal number of parts
        holding = self.holdings[holder]
        k = 1
        while k < len(top_amounts) and (holding / (k+1)) >= top_amounts[k-1] + EPS:
            k += 1
        # Step 4 - produce the allocation
        allocation = [self.holdings[holder] / k] * k

        # Step 5 - apply the allocation
        self.distribution[holder] = allocation
        return allocation != a_old

    def optimize_all_holders(self):
        """
        Optimizes all holders and returns true if there are still changes to the distribution
        """
        changes_made = False
        for holder in xrange(len(self.holdings)):
            if self.optimize_holder(holder):
                changes_made = True
        return changes_made

    def optimize(self):
        """ Optimizes all holders until distribution converges """
        c = 0
        while True:
            c += 1
            if not self.optimize_all_holders():
                break
        print 'converged after', c, 'cycles'

    def naive_staking_amout(self):
        """ Calculates how many atoms would have been staked with naive distribution,
            where each holder has one stake.
        """
        return sum(sorted(self.holdings)[-self.number_of_validators:])

    def optimized_staking_amout(self):
        """
        Calculates how many atoms would have been staked with the optimized distribution
        """
        all_amounts = [amount for amounts in self.distribution.values() for amount in amounts]
        top_amounts = sorted(all_amounts)[-self.number_of_validators:]
        return sum(top_amounts)

    def stake_loss(self):
        """
        Calculates loss of stake due to large stake holder optimizing their acounts
        """
        return (self.naive_staking_amout() - self.optimized_staking_amout())/self.naive_staking_amout()

print 'TEST SCENARIO'
scenario1 = Scenario(number_of_validators=5)
scenario1.set_holdings([1,1,1,1,1,1,2,2,2,2,6,8,12,13,15,23,160,140])
scenario1.optimize()
print scenario1.distribution
print 'Naive total stake', scenario1.naive_staking_amout()
print 'Optimized total stake', scenario1.optimized_staking_amout()

print '--------------------------------------------------'
print 'ETH SCENARIO'
scenario_eth = Scenario(number_of_validators=100)
with open('ethereum_sale.txt') as f:
    eth_holdings = [float(line) for line in f.xreadlines()]
scenario_eth.set_holdings(eth_holdings)
scenario_eth.optimize()
print 'Naive total stake', scenario_eth.naive_staking_amout()
print 'Optimized total stake', scenario_eth.optimized_staking_amout()
print '% stake loss due to optimization', scenario_eth.stake_loss() * 100